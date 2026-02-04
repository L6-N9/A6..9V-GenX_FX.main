"""
Gemini AI Service for GenX Trading Platform
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    """
    A service for interacting with the Google Gemini AI.

    This class provides methods to generate text, analyze market sentiment,
    and analyze trading signals using the Gemini Pro model.

    Attributes:
        api_key (str): The API key for the Gemini service.
        model: The primary generative model instance.
        chat_model: A separate model instance for chat functionalities.
        initialized (bool): True if the service has been successfully initialized.
    """

    def __init__(self):
        """
        Initializes the GeminiService.

        Retrieves the API key from environment variables and configures the
        Gemini models.

        Raises:
            ValueError: If the GEMINI_API_KEY environment variable is not set.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro")

        # Chat model for conversational analysis
        self.chat_model = genai.GenerativeModel("gemini-pro")

        self.initialized = False

    async def initialize(self) -> bool:
        """
        Initializes and tests the connection to the Gemini service.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            # Test connection by generating a short text
            response = await self.generate_text("Hello, testing connection")
            if response:
                logger.info("Gemini AI service initialized successfully")
                self.initialized = True
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            return False

    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generates text using the Gemini model based on a given prompt.

        Args:
            prompt (str): The input prompt for the model.
            max_tokens (int): The maximum number of tokens for the response.
                              Note: This argument is not directly used by the current
                              `generate_content` method but is kept for future compatibility.

        Returns:
            str: The generated text, or an empty string on failure.
        """
        try:
            # Use run_in_executor to run the synchronous SDK call in a non-blocking way
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.model.generate_content, prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini text generation error: {e}")
            return ""

    async def analyze_market_sentiment(self, text_data: List[str]) -> Dict[str, Any]:
        """
        Analyzes market sentiment from a list of text data (news, social media).

        Args:
            text_data (List[str]): A list of strings containing the text to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing the sentiment analysis,
                            including score, themes, confidence, and recommended action.
        """
        try:
            combined_text = "\n".join(text_data[:10])  # Limit to prevent token overflow

            prompt = f"""
            Analyze the market sentiment from the following financial news and social media posts.

            Text Data:
            {combined_text}

            Please provide:
            1. Overall sentiment score (-1 to 1, where -1 is very bearish, 1 is very bullish)
            2. Key themes mentioned
            3. Confidence level (0-1)
            4. Recommended trading action (buy/sell/hold)

            Return response in JSON format:
            {{
                "sentiment_score": float,
                "themes": [list of key themes],
                "confidence": float,
                "action": "buy/sell/hold",
                "reasoning": "brief explanation"
            }}
            """

            response_text = await self.generate_text(prompt)

            # Parse JSON response
            try:
                result = json.loads(response_text)
                return {
                    "sentiment_score": result.get("sentiment_score", 0),
                    "themes": result.get("themes", []),
                    "confidence": result.get("confidence", 0),
                    "action": result.get("action", "hold"),
                    "reasoning": result.get("reasoning", ""),
                    "timestamp": datetime.now(),
                }
            except json.JSONDecodeError:
                logger.warning(
                    f"Failed to parse JSON from Gemini sentiment response: {response_text}"
                )
                # Fallback parsing
                return {
                    "sentiment_score": 0,
                    "themes": [],
                    "confidence": 0,
                    "action": "hold",
                    "reasoning": response_text[
                        :200
                    ],  # Return a snippet of the raw response
                    "timestamp": datetime.now(),
                }

        except Exception as e:
            logger.error(f"Market sentiment analysis error: {e}")
            return {
                "sentiment_score": 0,
                "themes": [],
                "confidence": 0,
                "action": "hold",
                "reasoning": f"Error: {str(e)}",
                "timestamp": datetime.now(),
            }

    async def analyze_trading_signals(
        self, market_data: Dict[str, Any], news_data: List[str]
    ) -> Dict[str, Any]:
        """
        Analyzes market and news data to generate a trading signal.

        Args:
            market_data (Dict[str, Any]): A dictionary of market data (price, volume, etc.).
            news_data (List[str]): A list of recent news headlines.

        Returns:
            Dict[str, Any]: A dictionary containing the generated trading signal.
        """
        try:
            prompt = f"""
            As an expert trading analyst, analyze the following market data and news to generate trading signals.

            Market Data:
            - Symbol: {market_data.get('symbol', 'BTCUSDT')}
            - Current Price: {market_data.get('price', 'N/A')}
            - Volume: {market_data.get('volume', 'N/A')}
            - Technical Indicators: {market_data.get('indicators', {})}

            Recent News:
            {chr(10).join(news_data[:5])}

            Please provide:
            1. Signal strength (0-1)
            2. Direction (long/short/neutral)
            3. Entry price suggestion
            4. Stop loss level
            5. Take profit level
            6. Risk assessment

            Return response in JSON format:
            {{
                "signal_strength": float,
                "direction": "long/short/neutral",
                "entry_price": float,
                "stop_loss": float,
                "take_profit": float,
                "risk_level": "low/medium/high",
                "reasoning": "detailed explanation"
            }}
            """

            response_text = await self.generate_text(prompt)

            try:
                result = json.loads(response_text)
                return {
                    "signal_strength": result.get("signal_strength", 0),
                    "direction": result.get("direction", "neutral"),
                    "entry_price": result.get("entry_price", 0),
                    "stop_loss": result.get("stop_loss", 0),
                    "take_profit": result.get("take_profit", 0),
                    "risk_level": result.get("risk_level", "medium"),
                    "reasoning": result.get("reasoning", ""),
                    "timestamp": datetime.now(),
                }
            except json.JSONDecodeError:
                logger.warning(
                    f"Failed to parse JSON from Gemini signal response: {response_text}"
                )
                return {
                    "signal_strength": 0,
                    "direction": "neutral",
                    "entry_price": 0,
                    "stop_loss": 0,
                    "take_profit": 0,
                    "risk_level": "medium",
                    "reasoning": response_text[:200],
                    "timestamp": datetime.now(),
                }

        except Exception as e:
            logger.error(f"Trading signal analysis error: {e}")
            return {
                "signal_strength": 0,
                "direction": "neutral",
                "entry_price": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "risk_level": "high",
                "reasoning": f"Error: {str(e)}",
                "timestamp": datetime.now(),
            }

    async def chat_analysis(self, messages: List[Dict[str, str]]) -> str:
        """
        Performs interactive chat analysis for complex, conversational queries.

        Args:
            messages (List[Dict[str, str]]): A list of messages, each with a 'role'
                                             and 'content' key.

        Returns:
            str: The AI's response to the conversation.
        """
        try:
            # Format messages for Gemini
            conversation = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in messages]
            )

            response = await self.generate_text(conversation)
            return response

        except Exception as e:
            logger.error(f"Chat analysis error: {e}")
            return f"Error in chat analysis: {str(e)}"

    async def health_check(self) -> bool:
        """
        Checks if the Gemini service is healthy and responsive.

        Returns:
            bool: True if the service responds, False otherwise.
        """
        try:
            test_response = await self.generate_text("Health check test")
            return len(test_response) > 0
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

    async def shutdown(self):
        """Shuts down the Gemini service."""
        logger.info("Shutting down Gemini service...")
        self.initialized = False
