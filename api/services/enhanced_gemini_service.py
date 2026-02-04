"""
Enhanced Google Gemini AI integration for advanced market analysis, sentiment processing, and signal validation.
Provides contextual intelligence for trading decisions and market understanding.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

import google.generativeai as genai

from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class SentimentAnalysis:
    """
    Represents a structured result of a sentiment analysis query.

    Attributes:
        overall_sentiment (str): The dominant sentiment, e.g., "bullish", "bearish", "neutral".
        confidence (float): The model's confidence in the sentiment assessment (0.0 to 1.0).
        emotional_tone (str): The primary emotion detected, e.g., "fear", "greed".
        market_impact (str): The potential market impact, e.g., "high", "medium", "low".
        key_themes (List[str]): A list of key topics or themes driving the sentiment.
        risk_factors (List[str]): Identified risks or negative factors.
        opportunity_indicators (List[str]): Identified opportunities or positive factors.
        temporal_context (str): The time frame the sentiment likely applies to.
        source_reliability (float): An estimated reliability score for the source data.
    """

    overall_sentiment: str
    confidence: float
    emotional_tone: str
    market_impact: str
    key_themes: List[str]
    risk_factors: List[str]
    opportunity_indicators: List[str]
    temporal_context: str
    source_reliability: float


@dataclass
class SignalValidation:
    """
    Represents the result of a trading signal validation by the AI.

    Attributes:
        is_valid (bool): True if the signal is considered valid, False otherwise.
        confidence_adjustment (float): A multiplier to adjust the original signal's confidence.
        risk_assessment (str): The assessed risk level, e.g., "low", "medium", "high".
        market_context_score (float): A score representing how well the signal fits the market context.
        reasoning (str): A detailed explanation for the validation result.
        supporting_factors (List[str]): Factors that support the signal.
        warning_factors (List[str]): Factors that warn against the signal.
        recommended_position_size (float): A recommended position size multiplier (0.0 to 1.0).
    """

    is_valid: bool
    confidence_adjustment: float
    risk_assessment: str
    market_context_score: float
    reasoning: str
    supporting_factors: List[str]
    warning_factors: List[str]
    recommended_position_size: float


@dataclass
class MarketRegimeAnalysis:
    """
    Represents the analysis of the current market regime.

    Attributes:
        regime_type (str): The type of market regime, e.g., "trending", "ranging".
        trend_direction (str): The direction of the primary trend, e.g., "up", "down".
        volatility_level (str): The current level of market volatility.
        market_phase (str): The current market phase (e.g., Wyckoff phases).
        institutional_sentiment (str): The perceived sentiment of institutional players.
        retail_sentiment (str): The perceived sentiment of retail traders.
        news_flow_intensity (str): The intensity of market-related news flow.
    """

    regime_type: str
    trend_direction: str
    volatility_level: str
    market_phase: str
    institutional_sentiment: str
    retail_sentiment: str
    news_flow_intensity: str


class EnhancedGeminiService:
    """
    A service for interacting with Google's Gemini AI for advanced analysis.

    This service provides methods for sentiment analysis, signal validation,
    market regime analysis, and more, by building structured prompts and
    parsing JSON responses from the Gemini model.

    Attributes:
        model: The configured Gemini generative model instance.
        conversation_history (list): A history of the conversation with the model.
        market_context (dict): A dictionary to hold the current market context.
    """

    def __init__(self):
        """
        Initializes the EnhancedGeminiService.

        Configures the Gemini API key and sets up the generative model.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in the configuration.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            "gemini-1.5-pro"
        )  # Use the more advanced model
        self.conversation_history = []
        self.market_context = {}

    async def analyze_market_sentiment(
        self,
        news_articles: List[str],
        social_media_posts: List[str],
        instrument: str = "EUR/USD",
    ) -> SentimentAnalysis:
        """
        Performs a comprehensive sentiment analysis using news and social media.

        Args:
            news_articles (List[str]): A list of texts from news articles.
            social_media_posts (List[str]): A list of texts from social media.
            instrument (str): The trading instrument to focus the analysis on.

        Returns:
            SentimentAnalysis: A structured object containing the sentiment analysis results.
                               Returns a default object on failure.
        """
        try:
            # Prepare the analysis prompt
            prompt = self._build_sentiment_prompt(
                news_articles, social_media_posts, instrument
            )

            response = await self.model.generate_content_async(prompt)

            # Parse the structured response
            sentiment_data = self._parse_sentiment_response(response.text)

            return SentimentAnalysis(**sentiment_data)

        except Exception as e:
            logger.error(f"Error in market sentiment analysis: {e}")
            return self._get_default_sentiment()

    def _build_sentiment_prompt(
        self,
        news_articles: List[str],
        social_media_posts: List[str],
        instrument: str,
    ) -> str:
        """
        Builds the prompt for the comprehensive sentiment analysis.

        Args:
            news_articles (List[str]): A list of news article texts.
            social_media_posts (List[str]): A list of social media texts.
            instrument (str): The instrument of focus.

        Returns:
            str: The formatted prompt string.
        """
        news_text = "\n\n".join(news_articles[:10])  # Limit to avoid token limits
        social_text = "\n\n".join(social_media_posts[:20])

        return f"""
        As an expert financial market analyst, analyze the sentiment around {instrument} and the broader forex market based on the following information:

        NEWS ARTICLES:
        {news_text}

        SOCIAL MEDIA/FORUM POSTS:
        {social_text}

        Please provide a comprehensive analysis in the following JSON format:

        {{
            "overall_sentiment": "bullish|bearish|neutral",
            "confidence": 0.85,
            "emotional_tone": "fear|greed|uncertainty|optimism|panic|euphoria|caution",
            "market_impact": "high|medium|low",
            "key_themes": ["inflation concerns", "central bank policy", "geopolitical tensions"],
            "risk_factors": ["potential black swan events", "correlation breakdowns"],
            "opportunity_indicators": ["oversold conditions", "policy divergence"],
            "temporal_context": "short-term|medium-term|long-term",
            "source_reliability": 0.75
        }}

        Consider:
        1. The credibility and bias of sources
        2. The recency and relevance of information
        3. Correlation with historical market patterns
        4. Institutional vs retail sentiment divergence
        5. Potential market-moving events on the horizon
        6. Cross-asset implications (bonds, equities, commodities)
        7. Technical analysis context if mentioned
        8. Central bank communications and policy implications

        Provide only the JSON response without additional commentary.
        """

    async def validate_trading_signal(
        self,
        signal_data: Dict[str, Any],
        market_context: Dict[str, Any],
        current_sentiment: SentimentAnalysis,
        recent_news: List[str],
    ) -> SignalValidation:
        """
        Validates a trading signal using AI reasoning and multiple data points.

        Args:
            signal_data (Dict[str, Any]): The original trading signal data.
            market_context (Dict[str, Any]): Current market conditions (price, volatility, etc.).
            current_sentiment (SentimentAnalysis): The latest sentiment analysis result.
            recent_news (List[str]): A list of recent, relevant news headlines.

        Returns:
            SignalValidation: A structured object with the validation result.
                              Returns a default object on failure.
        """
        try:
            prompt = self._build_signal_validation_prompt(
                signal_data, market_context, current_sentiment, recent_news
            )

            response = await self.model.generate_content_async(prompt)
            validation_data = self._parse_validation_response(response.text)

            return SignalValidation(**validation_data)

        except Exception as e:
            logger.error(f"Error in signal validation: {e}")
            return self._get_default_validation()

    def _build_signal_validation_prompt(
        self,
        signal_data: Dict[str, Any],
        market_context: Dict[str, Any],
        sentiment: SentimentAnalysis,
        recent_news: List[str],
    ) -> str:
        """
        Builds the prompt for the trading signal validation.

        Args:
            signal_data (Dict[str, Any]): The signal data.
            market_context (Dict[str, Any]): The current market context.
            sentiment (SentimentAnalysis): The current sentiment analysis.
            recent_news (List[str]): Recent news headlines.

        Returns:
            str: The formatted prompt string.
        """
        news_summary = "\n".join(recent_news[:5])

        return f"""
        As an expert quantitative analyst and risk manager, evaluate this trading signal:

        SIGNAL DETAILS:
        - Instrument: {signal_data.get('instrument', 'Unknown')}
        - Action: {signal_data.get('action', 'Unknown')}
        - Confidence: {signal_data.get('confidence', 0)}
        - Generated by: {signal_data.get('model_type', 'AI Ensemble')}

        CURRENT MARKET CONTEXT:
        - Current Price: {market_context.get('current_price', 'N/A')}
        - Recent Volatility: {market_context.get('volatility', 'N/A')}
        - Volume: {market_context.get('volume', 'N/A')}
        - RSI: {market_context.get('rsi', 'N/A')}

        SENTIMENT ANALYSIS:
        - Overall Sentiment: {sentiment.overall_sentiment}
        - Confidence: {sentiment.confidence}
        - Market Impact: {sentiment.market_impact}
        - Key Themes: {', '.join(sentiment.key_themes)}

        RECENT NEWS HEADLINES:
        {news_summary}

        Evaluate this signal and provide your assessment in JSON format:

        {{
            "is_valid": true,
            "confidence_adjustment": 1.2,
            "risk_assessment": "low|medium|high|extreme",
            "market_context_score": 0.8,
            "reasoning": "Detailed explanation of your assessment",
            "supporting_factors": ["factor1", "factor2"],
            "warning_factors": ["warning1", "warning2"],
            "recommended_position_size": 0.75
        }}

        Consider:
        1. Signal-sentiment alignment
        2. Market regime appropriateness
        3. Risk-reward context
        4. Timing considerations
        5. Correlation with other assets
        6. News flow impact potential
        7. Technical vs fundamental divergence
        8. Liquidity conditions
        9. Volatility environment suitability
        10. Historical pattern recognition

        Provide only the JSON response.
        """

    async def analyze_market_regime(
        self,
        market_data: Dict[str, Any],
        economic_calendar: List[Dict],
        cross_asset_data: Dict[str, Any],
    ) -> MarketRegimeAnalysis:
        """
        Analyzes the current market regime and conditions.

        Args:
            market_data (Dict[str, Any]): Price, volume, and volatility data.
            economic_calendar (List[Dict]): A list of upcoming economic events.
            cross_asset_data (Dict[str, Any]): Data from other asset classes.

        Returns:
            MarketRegimeAnalysis: A structured object with the regime analysis.
                                  Returns a default object on failure.
        """
        try:
            prompt = self._build_regime_analysis_prompt(
                market_data, economic_calendar, cross_asset_data
            )

            response = await self.model.generate_content_async(prompt)
            regime_data = self._parse_regime_response(response.text)

            return MarketRegimeAnalysis(**regime_data)

        except Exception as e:
            logger.error(f"Error in market regime analysis: {e}")
            return self._get_default_regime()

    async def generate_adaptive_strategy_suggestions(
        self,
        current_performance: Dict[str, Any],
        market_conditions: MarketRegimeAnalysis,
        risk_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generates adaptive strategy suggestions based on performance and market conditions.

        Args:
            current_performance (Dict[str, Any]): Recent trading performance metrics.
            market_conditions (MarketRegimeAnalysis): The current market regime analysis.
            risk_metrics (Dict[str, Any]): Current risk exposure and metrics.

        Returns:
            Dict[str, Any]: A dictionary of strategy suggestions. Returns a default
                            response on failure.
        """
        try:
            prompt = f"""
            As an expert algorithmic trading strategist, analyze the current situation and provide adaptive strategy recommendations:

            CURRENT PERFORMANCE:
            - Win Rate: {current_performance.get('win_rate', 'N/A')}%
            - Profit Factor: {current_performance.get('profit_factor', 'N/A')}
            - Max Drawdown: {current_performance.get('max_drawdown', 'N/A')}%
            - Recent P&L: {current_performance.get('recent_pnl', 'N/A')}

            MARKET CONDITIONS:
            - Regime: {market_conditions.regime_type}
            - Trend: {market_conditions.trend_direction}
            - Volatility: {market_conditions.volatility_level}
            - Phase: {market_conditions.market_phase}

            RISK METRICS:
            - Current Exposure: {risk_metrics.get('current_exposure', 'N/A')}
            - VaR: {risk_metrics.get('var', 'N/A')}
            - Correlation Risk: {risk_metrics.get('correlation_risk', 'N/A')}

            Provide strategy recommendations in JSON format:

            {{
                "overall_recommendation": "increase_aggression|maintain_current|reduce_risk|defensive_mode",
                "position_sizing_adjustment": 1.2,
                "timeframe_optimization": "focus_on_shorter|current_ok|focus_on_longer",
                "instrument_preferences": ["EUR_USD", "GBP_USD"],
                "avoid_instruments": ["USD_JPY"],
                "risk_adjustments": {{
                    "max_risk_per_trade": 0.015,
                    "max_correlation": 0.6,
                    "stop_loss_multiplier": 1.1
                }},
                "strategy_modifications": [
                    "Increase momentum filter sensitivity",
                    "Add volatility breakout component"
                ],
                "market_timing_suggestions": [
                    "Avoid trading during first hour after major news",
                    "Increase position size during London-NY overlap"
                ],
                "reasoning": "Detailed explanation of recommendations"
            }}

            Focus on:
            1. Current market regime appropriateness
            2. Performance-based adjustments
            3. Risk-adjusted optimization
            4. Market microstructure considerations
            5. Behavioral finance insights

            Provide only the JSON response.
            """

            response = await self.model.generate_content_async(prompt)
            return self._parse_json_response(response.text)

        except Exception as e:
            logger.error(f"Error generating strategy suggestions: {e}")
            return {
                "overall_recommendation": "maintain_current",
                "reasoning": "Analysis unavailable",
            }

    async def analyze_economic_event_impact(
        self,
        event_details: Dict[str, Any],
        historical_patterns: List[Dict],
        current_positions: List[Dict],
    ) -> Dict[str, Any]:
        """
        Analyzes the potential impact of an upcoming economic event.

        Args:
            event_details (Dict[str, Any]): Details of the economic event.
            historical_patterns (List[Dict]): Historical market reactions to similar events.
            current_positions (List[Dict]): The current open trading positions.

        Returns:
            Dict[str, Any]: A dictionary containing the impact analysis. Returns a
                            default response on failure.
        """
        try:
            prompt = f"""
            As an expert in economic event analysis and market impact assessment, analyze this upcoming event:

            EVENT DETAILS:
            - Event: {event_details.get('name', 'Unknown')}
            - Time: {event_details.get('time', 'Unknown')}
            - Importance: {event_details.get('importance', 'Unknown')}
            - Forecast: {event_details.get('forecast', 'Unknown')}
            - Previous: {event_details.get('previous', 'Unknown')}
            - Currency: {event_details.get('currency', 'Unknown')}

            HISTORICAL PATTERNS:
            {json.dumps(historical_patterns[:3], indent=2)}

            CURRENT POSITIONS:
            {json.dumps(current_positions, indent=2)}

            Provide impact analysis in JSON format:

            {{
                "expected_volatility_increase": 1.5,
                "primary_affected_pairs": ["EUR_USD", "GBP_USD"],
                "secondary_affected_pairs": ["USD_JPY"],
                "time_horizon": "15_minutes|1_hour|4_hours|1_day",
                "directional_bias": "bullish_usd|bearish_usd|neutral",
                "confidence": 0.75,
                "position_recommendations": {{
                    "reduce_exposure": ["EUR_USD"],
                    "increase_stops": ["GBP_USD"],
                    "close_before_event": [],
                    "hedge_positions": []
                }},
                "trading_opportunities": [
                    "Volatility breakout strategy on EUR_USD",
                    "Mean reversion on initial spike"
                ],
                "risk_warnings": [
                    "Potential for multiple-standard-deviation moves",
                    "Increased slippage expected"
                ],
                "optimal_entry_timing": "pre_event|during_release|post_settlement",
                "reasoning": "Detailed analysis explanation"
            }}

            Consider:
            1. Historical precedent and patterns
            2. Current market positioning
            3. Cross-asset implications
            4. Volatility term structure impact
            5. Liquidity considerations
            6. Risk management requirements

            Provide only the JSON response.
            """

            response = await self.model.generate_content_async(prompt)
            return self._parse_json_response(response.text)

        except Exception as e:
            logger.error(f"Error analyzing economic event impact: {e}")
            return {
                "expected_volatility_increase": 1.0,
                "reasoning": "Analysis unavailable",
            }

    def _parse_sentiment_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parses a JSON object from the model's text response for sentiment analysis.

        Args:
            response_text (str): The raw text response from the Gemini model.

        Returns:
            Dict[str, Any]: The parsed JSON object as a dictionary.
        """
        return self._parse_json_response(
            response_text, self._get_default_sentiment_data
        )

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parses a JSON object from the model's text response for signal validation.

        Args:
            response_text (str): The raw text response from the Gemini model.

        Returns:
            Dict[str, Any]: The parsed JSON object as a dictionary.
        """
        return self._parse_json_response(
            response_text, self._get_default_validation_data
        )

    def _parse_regime_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parses a JSON object from the model's text response for market regime analysis.

        Args:
            response_text (str): The raw text response from the Gemini model.

        Returns:
            Dict[str, Any]: The parsed JSON object as a dictionary.
        """
        return self._parse_json_response(response_text, self._get_default_regime_data)

    def _parse_json_response(
        self, response_text: str, default_factory: Callable = dict
    ) -> Dict[str, Any]:
        """
        A generic and robust parser for extracting a JSON object from a string.

        Args:
            response_text (str): The string containing the JSON object.
            default_factory (Callable): A callable that returns a default value
                                        in case of a parsing error. Defaults to dict.

        Returns:
            Dict[str, Any]: The parsed dictionary, or a default value on failure.
        """
        try:
            # The model sometimes wraps the JSON in ```json ... ```
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            else:
                # Fallback to finding the first and last brace
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON object found in response")
                json_str = response_text[json_start:json_end]

            return json.loads(json_str)

        except (json.JSONDecodeError, ValueError, IndexError) as e:
            logger.error(f"Error parsing JSON response: {e}\nResponse: {response_text}")
            return default_factory()

    def _get_default_sentiment(self) -> SentimentAnalysis:
        """
        Returns a default, neutral sentiment analysis object.

        Returns:
            SentimentAnalysis: A default sentiment analysis instance.
        """
        return SentimentAnalysis(**self._get_default_sentiment_data())

    def _get_default_sentiment_data(self) -> Dict[str, Any]:
        """
        Returns a dictionary with default sentiment data.

        Returns:
            Dict[str, Any]: The default sentiment data.
        """
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.5,
            "emotional_tone": "uncertainty",
            "market_impact": "low",
            "key_themes": [],
            "risk_factors": [],
            "opportunity_indicators": [],
            "temporal_context": "short-term",
            "source_reliability": 0.5,
        }

    def _get_default_validation(self) -> SignalValidation:
        """
        Returns a default, permissive signal validation object.

        Returns:
            SignalValidation: A default signal validation instance.
        """
        return SignalValidation(**self._get_default_validation_data())

    def _get_default_validation_data(self) -> Dict[str, Any]:
        """
        Returns a dictionary with default signal validation data.

        Returns:
            Dict[str, Any]: The default validation data.
        """
        return {
            "is_valid": True,
            "confidence_adjustment": 1.0,
            "risk_assessment": "medium",
            "market_context_score": 0.5,
            "reasoning": "Analysis unavailable",
            "supporting_factors": [],
            "warning_factors": [],
            "recommended_position_size": 0.5,
        }

    def _get_default_regime(self) -> MarketRegimeAnalysis:
        """
        Returns a default, neutral market regime analysis object.

        Returns:
            MarketRegimeAnalysis: A default market regime instance.
        """
        return MarketRegimeAnalysis(**self._get_default_regime_data())

    def _get_default_regime_data(self) -> Dict[str, Any]:
        """
        Returns a dictionary with default market regime data.

        Returns:
            Dict[str, Any]: The default regime data.
        """
        return {
            "regime_type": "ranging",
            "trend_direction": "sideways",
            "volatility_level": "normal",
            "market_phase": "accumulation",
            "institutional_sentiment": "neutral",
            "retail_sentiment": "neutral",
            "news_flow_intensity": "normal",
        }

    def _build_regime_analysis_prompt(
        self,
        market_data: Dict[str, Any],
        economic_calendar: List[Dict],
        cross_asset_data: Dict[str, Any],
    ) -> str:
        """
        Builds the prompt for the market regime analysis.

        Args:
            market_data (Dict[str, Any]): The market data.
            economic_calendar (List[Dict]): The economic calendar events.
            cross_asset_data (Dict[str, Any]): The cross-asset data.

        Returns:
            str: The formatted prompt string.
        """
        events_summary = "\n".join(
            [
                f"- {event.get('name', 'Unknown')} at {event.get('time', 'Unknown')}"
                for event in economic_calendar[:5]
            ]
        )

        return f"""
        As an expert macro analyst, analyze the current market regime based on this comprehensive data:

        FOREX MARKET DATA:
        {json.dumps(market_data, indent=2)}

        UPCOMING ECONOMIC EVENTS:
        {events_summary}

        CROSS-ASSET DATA:
        {json.dumps(cross_asset_data, indent=2)}

        Provide regime analysis in JSON format:

        {{
            "regime_type": "trending|ranging|volatile|calm|crisis",
            "trend_direction": "up|down|sideways",
            "volatility_level": "low|normal|high|extreme",
            "market_phase": "accumulation|distribution|markup|markdown",
            "institutional_sentiment": "risk_on|risk_off|neutral",
            "retail_sentiment": "risk_on|risk_off|neutral",
            "news_flow_intensity": "light|normal|heavy|overwhelming"
        }}

        Consider all available information to determine the current market environment.
        Provide only the JSON response.
        """


# Factory function
def create_enhanced_gemini_service() -> EnhancedGeminiService:
    """
    Factory function to create an instance of the EnhancedGeminiService.

    Returns:
        EnhancedGeminiService: An instance of the service.
    """
    return EnhancedGeminiService()
