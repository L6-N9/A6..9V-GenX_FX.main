"""
TCP/IP Socket Communication Service for MT4/MT5 Expert Advisor Integration.
Provides real-time signal transmission and trade feedback between Python AI and MQL EAs.
"""

import asyncio
import json
import logging
import socket
import struct
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """
    Represents a trading signal to be sent to an Expert Advisor (EA).

    Attributes:
        signal_id (str): A unique identifier for the signal.
        instrument (str): The trading instrument or symbol (e.g., 'EURUSD').
        action (str): The action to be taken, one of "BUY", "SELL", "CLOSE", "CLOSE_ALL".
        volume (float): The trade volume or lot size.
        stop_loss (Optional[float]): The stop-loss price.
        take_profit (Optional[float]): The take-profit price.
        magic_number (int): The magic number for the EA to identify trades.
        comment (str): A comment for the trade.
        timestamp (datetime): The time the signal was generated.
        confidence (float): The confidence level of the signal (0.0 to 1.0).
    """

    signal_id: str
    instrument: str
    action: str  # "BUY", "SELL", "CLOSE", "CLOSE_ALL"
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    magic_number: int = 12345
    comment: str = "GenX AI Signal"
    timestamp: Optional[datetime] = None
    confidence: float = 0.0

    def __post_init__(self):
        """Sets the timestamp to now if it's not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the signal object to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the signal.
        """
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradingSignal":
        """
        Creates a TradingSignal instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary to create the object from.

        Returns:
            TradingSignal: An instance of the TradingSignal class.
        """
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class TradeResult:
    """
    Represents the result of a trade execution received from an EA.

    Attributes:
        signal_id (str): The ID of the signal that triggered this trade.
        ticket (Optional[int]): The ticket number of the executed trade, if successful.
        success (bool): True if the trade was executed successfully, False otherwise.
        error_code (int): The error code from the trading terminal, if any.
        error_message (str): The error message, if any.
        execution_price (Optional[float]): The price at which the trade was executed.
        execution_time (datetime): The timestamp of the execution.
        slippage (float): The slippage in pips.
    """

    signal_id: str
    ticket: Optional[int]
    success: bool
    error_code: int = 0
    error_message: str = ""
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None
    slippage: float = 0.0

    def __post_init__(self):
        """Sets the execution time to now if it's not provided."""
        if self.execution_time is None:
            self.execution_time = datetime.utcnow()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeResult":
        """
        Creates a TradeResult instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary to create the object from.

        Returns:
            TradeResult: An instance of the TradeResult class.
        """
        if "execution_time" in data and isinstance(data["execution_time"], str):
            data["execution_time"] = datetime.fromisoformat(data["execution_time"])
        return cls(**data)


@dataclass
class AccountStatus:
    """
    Represents the account status update received from an EA.

    Attributes:
        balance (float): The account balance.
        equity (float): The account equity.
        margin (float): The margin used.
        free_margin (float): The free margin available.
        margin_level (float): The margin level percentage.
        profit (float): The current floating profit/loss.
        open_positions (int): The number of open positions.
        timestamp (datetime): The timestamp of the status update.
    """

    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    profit: float
    open_positions: int
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Sets the timestamp to now if it's not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountStatus":
        """
        Creates an AccountStatus instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary to create the object from.

        Returns:
            AccountStatus: An instance of the AccountStatus class.
        """
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MessageProtocol:
    """
    Handles the encoding and decoding of messages for EA communication.

    The protocol uses a simple format: a 4-byte network-ordered integer
    representing the length of the JSON payload, followed by the UTF-8
    encoded JSON payload itself.
    """

    @staticmethod
    def encode_message(message_type: str, data: Dict[str, Any]) -> bytes:
        """
        Encodes a message into bytes for transmission to the EA.

        Args:
            message_type (str): The type of the message (e.g., "SIGNAL", "COMMAND").
            data (Dict[str, Any]): The data payload for the message.

        Returns:
            bytes: The encoded message, ready for socket transmission.
        """
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        json_data = json.dumps(message).encode("utf-8")
        # Prepend the length of the JSON data as a 4-byte integer
        length = struct.pack("!I", len(json_data))

        return length + json_data

    @staticmethod
    def decode_message(data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decodes a message received from the EA.

        Args:
            data (bytes): The raw byte string received from the socket.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the decoded
                                      message, or None if the message is
                                      incomplete or invalid.
        """
        try:
            if len(data) < 4:
                return None  # Not enough data for the length prefix

            # Extract the length of the JSON payload
            length = struct.unpack("!I", data[:4])[0]

            if len(data) < 4 + length:
                return None  # The full message has not been received yet

            # Extract and decode the JSON data
            json_data = data[4 : 4 + length].decode("utf-8")
            message = json.loads(json_data)

            return message

        except (struct.error, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error decoding message: {e}")
            return None


class EAConnection:
    """
    Handles an individual connection from a single EA client.

    This class manages the socket, receives data in a separate thread,
    processes the incoming message buffer, and sends signals/commands.

    Attributes:
        socket (socket.socket): The client socket object.
        address (tuple): The client's address (host, port).
        server (EAServer): A reference to the main server instance.
        is_connected (bool): True if the connection is active.
        buffer (bytes): A buffer for storing incoming data.
        ea_info (dict): Information about the connected EA (e.g., account number).
        receive_thread (threading.Thread): The thread for receiving messages.
    """

    def __init__(
        self, client_socket: socket.socket, address: tuple, server: "EAServer"
    ):
        """
        Initializes an EA connection.

        Args:
            client_socket (socket.socket): The socket for the connected client.
            address (tuple): The address of the client.
            server (EAServer): The parent server instance.
        """
        self.socket = client_socket
        self.address = address
        self.server = server
        self.is_connected = True
        self.buffer = b""
        self.ea_info = {}

        # Start a daemon thread to listen for messages from the EA
        self.receive_thread = threading.Thread(
            target=self._receive_messages, daemon=True
        )
        self.receive_thread.start()

        logger.info(f"New EA connection from {address}")

    def _receive_messages(self):
        """
        Continuously receives messages from the EA in a dedicated thread.

        This loop reads data from the socket, adds it to a buffer, and
        processes the buffer. It handles timeouts and disconnection.
        """
        try:
            while self.is_connected:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        # An empty recv indicates the client has disconnected
                        break

                    self.buffer += data
                    self._process_buffer()

                except socket.timeout:
                    continue  # Timeout is expected, just continue listening
                except Exception as e:
                    logger.error(f"Error receiving from EA {self.address}: {e}")
                    break

        except Exception as e:
            logger.error(f"Error in receive thread for {self.address}: {e}")
        finally:
            self._disconnect()

    def _process_buffer(self):
        """
        Processes the incoming data buffer to extract complete messages.

        It repeatedly decodes messages from the buffer until an incomplete
        message is found. Completed messages are handled by the server.
        """
        while len(self.buffer) >= 4:
            # Attempt to decode a message from the start of the buffer
            message = MessageProtocol.decode_message(self.buffer)

            if message is None:
                break  # Incomplete message, wait for more data

            # A message was successfully decoded, remove it from the buffer
            length = struct.unpack("!I", self.buffer[:4])[0]
            self.buffer = self.buffer[4 + length :]

            # Schedule the message handler to run in the server's asyncio loop
            asyncio.run_coroutine_threadsafe(
                self.server._handle_message(message, self), self.server.loop
            )

    async def send_signal(self, signal: TradingSignal) -> bool:
        """
        Sends a trading signal to the connected EA.

        Args:
            signal (TradingSignal): The signal to send.

        Returns:
            bool: True if the signal was sent successfully, False otherwise.
        """
        try:
            message_data = signal.to_dict()
            encoded_message = MessageProtocol.encode_message("SIGNAL", message_data)

            self.socket.sendall(encoded_message)
            logger.info(
                f"Signal sent to EA {self.address}: {signal.action} {signal.instrument}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending signal to EA {self.address}: {e}")
            self._disconnect()
            return False

    async def send_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Sends a command to the connected EA.

        Args:
            command (str): The command to send (e.g., "GET_STATUS").
            params (Dict[str, Any], optional): Parameters for the command.

        Returns:
            bool: True if the command was sent successfully, False otherwise.
        """
        try:
            command_data = {"command": command, "parameters": params or {}}
            encoded_message = MessageProtocol.encode_message("COMMAND", command_data)

            self.socket.sendall(encoded_message)
            logger.info(f"Command sent to EA {self.address}: {command}")
            return True

        except Exception as e:
            logger.error(f"Error sending command to EA {self.address}: {e}")
            self._disconnect()
            return False

    def _disconnect(self):
        """
        Closes the connection to the EA and notifies the server.
        """
        if self.is_connected:
            self.is_connected = False
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except OSError:
                pass  # Ignore errors on close, socket might already be closed

            self.server._remove_connection(self)
            logger.info(f"EA disconnected: {self.address}")


class EAServer:
    """
    A TCP server that listens for and manages connections from EAs.

    This server can accept multiple concurrent EA connections, handle incoming
    messages, and broadcast signals or commands.

    Attributes:
        host (str): The host IP address to bind to.
        port (int): The port to listen on.
        server_socket (socket.socket): The main server socket.
        connections (List[EAConnection]): A list of active EA connections.
        is_running (bool): True if the server is running.
        loop (asyncio.AbstractEventLoop): The asyncio event loop.
        callbacks (Dict[str, List]): A dictionary to store callback functions
                                     for different message types.
        signal_queue (Queue): A thread-safe queue for signals to be broadcast.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 9090):
        """
        Initializes the EAServer.

        Args:
            host (str): The host IP to bind to. Defaults to "0.0.0.0".
            port (int): The port to listen on. Defaults to 9090.
        """
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.connections: List[EAConnection] = []
        self.is_running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        # Callbacks for different message types
        self.callbacks: Dict[str, List[Callable]] = {
            "TRADE_RESULT": [],
            "ACCOUNT_STATUS": [],
            "HEARTBEAT": [],
            "ERROR": [],
        }

        # Signal queue for broadcasting from other threads
        self.signal_queue: Queue[TradingSignal] = Queue()

    async def start(self):
        """
        Starts the EA server, binds it to the host and port, and begins
        listening for connections.

        Raises:
            Exception: If the server fails to start.
        """
        try:
            self.loop = asyncio.get_running_loop()

            # Create and configure the server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.server_socket.settimeout(1.0)  # Use a timeout for non-blocking accept

            self.is_running = True
            logger.info(f"EA Server started on {self.host}:{self.port}")

            # Start the main loop for accepting connections
            await self._accept_connections()

        except Exception as e:
            logger.error(f"Error starting EA server: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stops the EA server and closes all active connections."""
        if not self.is_running:
            return
        self.is_running = False

        # Disconnect all EAs
        for connection in self.connections[:]:  # Iterate over a copy
            connection._disconnect()

        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

        logger.info("EA Server stopped")

    async def _accept_connections(self):
        """
        The main server loop for accepting new EA connections.
        """
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.settimeout(30.0)  # Set a timeout for client operations

                # Create a new connection handler for the client
                connection = EAConnection(client_socket, address, self)
                self.connections.append(connection)

            except socket.timeout:
                # This is expected due to the non-blocking socket.
                # Use this opportunity to process the signal queue.
                await self._process_signal_queue()
                await asyncio.sleep(0.1)  # Prevent busy-waiting
            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting connection: {e}")
                await asyncio.sleep(1)

    async def _process_signal_queue(self):
        """
        Processes any signals that have been queued for broadcasting.
        """
        try:
            while not self.signal_queue.empty():
                signal = self.signal_queue.get_nowait()
                await self.broadcast_signal(signal)
        except Empty:
            pass  # Queue is empty, which is normal

    def _remove_connection(self, connection: EAConnection):
        """
        Removes a disconnected connection from the active list.

        Args:
            connection (EAConnection): The connection to remove.
        """
        if connection in self.connections:
            self.connections.remove(connection)

    async def _handle_message(self, message: Dict[str, Any], connection: EAConnection):
        """
        Handles a decoded message from an EA connection.

        This method routes the message to the appropriate handler based on its type
        and triggers any registered callbacks.

        Args:
            message (Dict[str, Any]): The decoded message.
            connection (EAConnection): The connection from which the message originated.
        """
        try:
            message_type = message.get("type")
            data = message.get("data", {})

            if message_type == "TRADE_RESULT":
                trade_result = TradeResult.from_dict(data)
                await self._notify_callbacks("TRADE_RESULT", trade_result, connection)
            elif message_type == "ACCOUNT_STATUS":
                account_status = AccountStatus.from_dict(data)
                await self._notify_callbacks(
                    "ACCOUNT_STATUS", account_status, connection
                )
            elif message_type == "HEARTBEAT":
                connection.ea_info.update(data)
                await self._notify_callbacks("HEARTBEAT", data, connection)
            elif message_type == "ERROR":
                logger.error(f"EA Error from {connection.address}: {data}")
                await self._notify_callbacks("ERROR", data, connection)
            elif message_type == "EA_INFO":
                connection.ea_info = data
                logger.info(f"EA Info from {connection.address}: {data}")
            else:
                logger.warning(
                    f"Unknown message type from EA {connection.address}: {message_type}"
                )

        except Exception as e:
            logger.error(f"Error handling message from EA {connection.address}: {e}")

    async def _notify_callbacks(
        self, message_type: str, data: Any, connection: EAConnection
    ):
        """
        Notifies all registered callbacks for a given message type.

        Args:
            message_type (str): The type of the message.
            data (Any): The data payload to pass to the callback.
            connection (EAConnection): The connection associated with the event.
        """
        for callback in self.callbacks.get(message_type, []):
            try:
                # Check if the callback is a coroutine function
                if asyncio.iscoroutinefunction(callback):
                    await callback(data, connection)
                else:
                    callback(data, connection)
            except Exception as e:
                logger.error(f"Error in callback for {message_type}: {e}")

    def subscribe_to_trade_results(
        self, callback: Callable[[TradeResult, EAConnection], Any]
    ):
        """
        Subscribes a callback function to receive trade execution results.

        Args:
            callback: A function or coroutine to be called with TradeResult and EAConnection.
        """
        self.callbacks["TRADE_RESULT"].append(callback)

    def subscribe_to_account_status(
        self, callback: Callable[[AccountStatus, EAConnection], Any]
    ):
        """
        Subscribes a callback function to receive account status updates.

        Args:
            callback: A function or coroutine to be called with AccountStatus and EAConnection.
        """
        self.callbacks["ACCOUNT_STATUS"].append(callback)

    def subscribe_to_heartbeat(self, callback: Callable[[Dict, EAConnection], Any]):
        """
        Subscribes a callback function to receive EA heartbeat messages.

        Args:
            callback: A function or coroutine to be called with heartbeat data and EAConnection.
        """
        self.callbacks["HEARTBEAT"].append(callback)

    def subscribe_to_errors(self, callback: Callable[[Dict, EAConnection], Any]):
        """
        Subscribes a callback function to receive EA error messages.

        Args:
            callback: A function or coroutine to be called with error data and EAConnection.
        """
        self.callbacks["ERROR"].append(callback)

    async def send_signal_to_ea(
        self, signal: TradingSignal, ea_address: Optional[tuple] = None
    ) -> bool:
        """
        Sends a signal to a specific EA or broadcasts to all.

        Args:
            signal (TradingSignal): The signal to send.
            ea_address (Optional[tuple]): The address of a specific EA. If None,
                                          the signal is broadcast to all.

        Returns:
            bool: True if the signal was sent to at least one EA, False otherwise.
        """
        if ea_address:
            # Send to a specific EA
            connection = next(
                (c for c in self.connections if c.address == ea_address), None
            )
            if connection:
                return await connection.send_signal(signal)
            logger.warning(f"EA with address {ea_address} not found.")
            return False
        else:
            # Broadcast to all EAs
            return await self.broadcast_signal(signal)

    async def broadcast_signal(self, signal: TradingSignal) -> bool:
        """
        Broadcasts a trading signal to all connected EAs.

        Args:
            signal (TradingSignal): The signal to broadcast.

        Returns:
            bool: True if the signal was sent to at least one EA, False otherwise.
        """
        if not self.connections:
            logger.warning("No EAs connected to receive signal, queueing instead.")
            self.queue_signal(signal)
            return False

        tasks = [conn.send_signal(signal) for conn in self.connections]
        results = await asyncio.gather(*tasks)
        success_count = sum(1 for r in results if r)

        logger.info(
            f"Signal broadcasted to {success_count}/{len(self.connections)} EAs"
        )
        return success_count > 0

    async def send_command_to_all(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Sends a command to all connected EAs concurrently.

        Args:
            command (str): The command to send.
            params (Optional[Dict[str, Any]]): Parameters for the command.

        Returns:
            int: The number of EAs the command was successfully sent to.
        """
        tasks = [conn.send_command(command, params) for conn in self.connections]
        results = await asyncio.gather(*tasks)
        return sum(1 for r in results if r)

    def get_connected_eas(self) -> List[Dict[str, Any]]:
        """
        Gets information about all currently connected EAs.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing
                                  details about a connected EA.
        """
        return [
            {
                "address": conn.address,
                "connected": conn.is_connected,
                "info": conn.ea_info,
            }
            for conn in self.connections
        ]

    def queue_signal(self, signal: TradingSignal):
        """
        Queues a signal for broadcasting. This method is thread-safe.

        Args:
            signal (TradingSignal): The signal to be queued.
        """
        self.signal_queue.put(signal)


class EAClient:
    """
    A client for connecting to the EAServer, primarily for testing purposes.

    This client can simulate an EA by connecting to the server and sending
    messages like trade results and account status updates.

    Attributes:
        host (str): The server host to connect to.
        port (int): The server port.
        socket (socket.socket): The client socket.
        is_connected (bool): True if the client is connected.
    """

    def __init__(self, host: str = "localhost", port: int = 9090):
        """
        Initializes the EAClient.

        Args:
            host (str): The server host.
            port (int): The server port.
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Connects to the EA server and sends initial EA info.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True

            # Send identifying information to the server
            ea_info = {
                "name": "Test EA",
                "version": "1.0",
                "account": "12345",
                "broker": "Test Broker",
            }
            await self.send_message("EA_INFO", ea_info)
            logger.info(f"Connected to EA server at {self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Error connecting to EA server: {e}")
            return False

    async def disconnect(self):
        """Disconnects from the EA server."""
        if self.is_connected and self.socket:
            self.socket.close()
            self.is_connected = False
            logger.info("Disconnected from EA server")

    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """
        Encodes and sends a message to the EA server.

        Args:
            message_type (str): The type of the message.
            data (Dict[str, Any]): The message payload.

        Raises:
            Exception: If the client is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to EA server")

        encoded_message = MessageProtocol.encode_message(message_type, data)
        self.socket.sendall(encoded_message)

    async def send_trade_result(
        self,
        signal_id: str,
        success: bool,
        ticket: Optional[int] = None,
        error: str = "",
    ):
        """
        Sends a trade execution result to the server.

        Args:
            signal_id (str): The ID of the signal being responded to.
            success (bool): Whether the trade was successful.
            ticket (Optional[int]): The trade ticket number.
            error (str): Any error message.
        """
        result_data = {
            "signal_id": signal_id,
            "success": success,
            "ticket": ticket,
            "error_message": error,
            "execution_time": datetime.utcnow().isoformat(),
        }
        await self.send_message("TRADE_RESULT", result_data)

    async def send_account_status(self, balance: float, equity: float, margin: float):
        """
        Sends an account status update to the server.

        Args:
            balance (float): The current account balance.
            equity (float): The current account equity.
            margin (float): The current margin used.
        """
        status_data = {
            "balance": balance,
            "equity": equity,
            "margin": margin,
            "free_margin": equity - margin,
            "margin_level": (equity / margin * 100) if margin > 0 else 0,
            "profit": equity - balance,
            "open_positions": 3,  # Example value
        }
        await self.send_message("ACCOUNT_STATUS", status_data)


# Factory functions
async def create_ea_server(host: str = "0.0.0.0", port: int = 9090) -> EAServer:
    """
    Factory function to create and start an EAServer instance.

    Args:
        host (str): The host to bind the server to.
        port (int): The port to listen on.

    Returns:
        EAServer: An initialized and started EAServer instance.
    """
    server = EAServer(host, port)
    # The start method runs the server's main loop, so it should be run
    # as a background task if more code needs to execute.
    # For a simple factory, we assume it's being started and managed elsewhere.
    # await server.start()
    return server


async def create_ea_client(host: str = "localhost", port: int = 9090) -> EAClient:
    """
    Factory function to create and connect an EAClient instance.

    Args:
        host (str): The server host to connect to.
        port (int): The server port.

    Returns:
        EAClient: A connected EAClient instance.
    """
    client = EAClient(host, port)
    await client.connect()
    return client
