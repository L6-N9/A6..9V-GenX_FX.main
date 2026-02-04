#!/usr/bin/env python3
"""
GenX FX 24/7 Windows Service
Runs the trading backend as a Windows service for continuous operation
"""

import logging
import os
import socket
import sys
import time
from pathlib import Path

import servicemanager
import win32event
import win32service
import win32serviceutil

# Add the api directory to Python path
sys.path.append(str(Path(__file__).parent / "api"))


class GenX24_7Service(win32serviceutil.ServiceFramework):
    """
    A Windows Service class for the GenX FX 24/7 Backend.
    This class handles the service lifecycle, including starting, stopping,
    and running the main application logic.
    """

    _svc_name_ = "GenX24_7Backend"
    _svc_display_name_ = "GenX FX 24/7 Trading Backend"
    _svc_description_ = (
        "GenX FX Trading Platform 24/7 Backend Service with Gold Signal Generation"
    )

    def __init__(self, args):
        """
        Initializes the Windows service.

        Args:
            args: Command-line arguments passed to the service.
        """
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = False

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("C:\\GenX_FX\\logs\\genx-service.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def SvcStop(self):
        """
        Called when the service is asked to stop.
        """
        self.logger.info("🛑 Stopping GenX FX 24/7 Service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        """
        Called when the service is asked to run.
        """
        self.logger.info("🚀 Starting GenX FX 24/7 Service...")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )

        self.is_running = True
        self.main()

    def main(self):
        """
        The main loop of the service, which runs the backend application.
        """
        try:
            # Import and run the backend
            import asyncio

            from genx_24_7_backend import GenX24_7Backend

            # Create backend instance
            backend = GenX24_7Backend()

            # Run the backend
            asyncio.run(backend.start())

        except Exception as e:
            self.logger.error(f"❌ Service error: {e}")
            servicemanager.LogErrorMsg(f"GenX FX Service Error: {e}")


def install_service():
    """
    Installs the Windows service.
    """
    try:
        win32serviceutil.InstallService(
            GenX24_7Service._svc_reg_class_,
            GenX24_7Service._svc_name_,
            GenX24_7Service._svc_display_name_,
            description=GenX24_7Service._svc_description_,
        )
        print("✅ GenX FX 24/7 Service installed successfully")
        print("   Use 'net start GenX24_7Backend' to start the service")
        print("   Use 'net stop GenX24_7Backend' to stop the service")
    except Exception as e:
        print(f"❌ Failed to install service: {e}")


def remove_service():
    """
    Removes the Windows service.
    """
    try:
        win32serviceutil.RemoveService(GenX24_7Service._svc_name_)
        print("✅ GenX FX 24/7 Service removed successfully")
    except Exception as e:
        print(f"❌ Failed to remove service: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GenX24_7Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GenX24_7Service)
