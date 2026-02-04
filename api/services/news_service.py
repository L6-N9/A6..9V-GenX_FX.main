"""
News Integration Service for GenX Trading Platform
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import finnhub
from alpha_vantage.fundamentaldata import FundamentalData
from newsapi import NewsApiClient

logger = logging.getLogger(__name__)


class NewsService:
    """
    A service for fetching and aggregating financial news from multiple sources.

    This class initializes clients for various news APIs and provides methods
    to get news for different market categories like crypto, stocks, and forex.

    Attributes:
        newsapi_client: Client for the NewsAPI.org service.
        finnhub_client: Client for the Finnhub.io service.
        alphavantage: Client for the Alpha Vantage service.
        initialized (bool): True if the service has been initialized.
    """

    def __init__(self):
        """
        Initializes the NewsService.

        It retrieves API keys from environment variables and sets up the
        respective client libraries.
        """
        # API Keys
        self.newsdata_key = os.getenv("NEWSDATA_API_KEY")
        self.alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY")
        self.newsapi_key = os.getenv("NEWSAPI_ORG_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.fmp_key = os.getenv("FMP_API_KEY")

        # Initialize clients
        self.newsapi_client = (
            NewsApiClient(api_key=self.newsapi_key) if self.newsapi_key else None
        )
        self.finnhub_client = (
            finnhub.Client(api_key=self.finnhub_key) if self.finnhub_key else None
        )
        self.alphavantage = (
            FundamentalData(key=self.alphavantage_key)
            if self.alphavantage_key
            else None
        )

        self.initialized = False

        # Keywords for categorization (currently not used but defined)
        self.crypto_keywords = [
            "bitcoin",
            "ethereum",
            "cryptocurrency",
            "blockchain",
            "defi",
            "nft",
            "crypto",
            "btc",
            "eth",
            "altcoin",
            "coinbase",
            "binance",
        ]
        self.stock_keywords = [
            "stock market",
            "nasdaq",
            "dow jones",
            "s&p 500",
            "earnings",
            "fed",
            "inflation",
            "interest rates",
            "wall street",
            "trading",
            "investment",
        ]
        self.forex_keywords = [
            "forex",
            "currency",
            "usd",
            "eur",
            "gbp",
            "jpy",
            "exchange rate",
            "federal reserve",
            "central bank",
            "dollar",
            "euro",
        ]

    async def initialize(self) -> bool:
        """
        Initializes the news service by testing connections to the APIs.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            # Test connections
            if self.newsapi_client:
                await self._test_newsapi()

            if self.finnhub_client:
                await self._test_finnhub()

            logger.info("News service initialized successfully")
            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize news service: {e}")
            return False

    async def get_crypto_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Aggregates cryptocurrency news from multiple sources.

        Args:
            limit (int): The maximum number of news articles to return.

        Returns:
            List[Dict[str, Any]]: A sorted and deduplicated list of news articles.
        """
        all_news = []

        # NewsAPI
        if self.newsapi_client:
            newsapi_articles = await self._get_newsapi_articles(
                "cryptocurrency", limit=20
            )
            all_news.extend(newsapi_articles)

        # Finnhub
        if self.finnhub_client:
            finnhub_articles = await self._get_finnhub_news("crypto", limit=15)
            all_news.extend(finnhub_articles)

        # NewsData.io
        if self.newsdata_key:
            newsdata_articles = await self._get_newsdata_articles(
                "cryptocurrency", limit=15
            )
            all_news.extend(newsdata_articles)

        # Remove duplicates and sort by date
        unique_news = self._remove_duplicates(all_news)
        sorted_news = sorted(unique_news, key=lambda x: x["published_at"], reverse=True)

        return sorted_news[:limit]

    async def get_stock_news(
        self, symbol: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Aggregates stock market news, optionally for a specific symbol.

        Args:
            symbol (Optional[str]): The stock symbol (e.g., "AAPL"). If None,
                                    general market news is fetched.
            limit (int): The maximum number of news articles to return.

        Returns:
            List[Dict[str, Any]]: A sorted and deduplicated list of news articles.
        """
        all_news = []

        # NewsAPI
        if self.newsapi_client:
            query = f"{symbol} stock" if symbol else "stock market"
            newsapi_articles = await self._get_newsapi_articles(query, limit=20)
            all_news.extend(newsapi_articles)

        # Finnhub
        if self.finnhub_client:
            if symbol:
                finnhub_articles = await self._get_finnhub_company_news(
                    symbol, limit=15
                )
            else:
                finnhub_articles = await self._get_finnhub_news("general", limit=15)
            all_news.extend(finnhub_articles)

        # Alpha Vantage
        if self.alphavantage and symbol:
            av_articles = await self._get_alphavantage_news(symbol, limit=10)
            all_news.extend(av_articles)

        # Remove duplicates and sort
        unique_news = self._remove_duplicates(all_news)
        sorted_news = sorted(unique_news, key=lambda x: x["published_at"], reverse=True)

        return sorted_news[:limit]

    async def get_forex_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Aggregates forex and currency-related news.

        Args:
            limit (int): The maximum number of news articles to return.

        Returns:
            List[Dict[str, Any]]: A sorted and deduplicated list of news articles.
        """
        all_news = []

        # NewsAPI
        if self.newsapi_client:
            newsapi_articles = await self._get_newsapi_articles(
                "forex currency", limit=20
            )
            all_news.extend(newsapi_articles)

        # Finnhub
        if self.finnhub_client:
            finnhub_articles = await self._get_finnhub_news("forex", limit=10)
            all_news.extend(finnhub_articles)

        # Remove duplicates and sort
        unique_news = self._remove_duplicates(all_news)
        sorted_news = sorted(unique_news, key=lambda x: x["published_at"], reverse=True)

        return sorted_news[:limit]

    async def get_market_sentiment_news(self) -> Dict[str, Any]:
        """
        Gathers a broad range of news for general market sentiment analysis.

        Returns:
            Dict[str, Any]: A dictionary containing aggregated news data, including
                            counts and combined text for analysis.
        """
        try:
            # Get news from all categories
            crypto_news = await self.get_crypto_news(limit=20)
            stock_news = await self.get_stock_news(limit=20)
            forex_news = await self.get_forex_news(limit=10)

            # Combine all news
            all_news = crypto_news + stock_news + forex_news

            # Extract headlines and descriptions for sentiment analysis
            news_texts = [
                f"{article['title']} {article.get('description', '')}"
                for article in all_news
            ]

            return {
                "news_count": len(all_news),
                "crypto_news_count": len(crypto_news),
                "stock_news_count": len(stock_news),
                "forex_news_count": len(forex_news),
                "news_texts": news_texts,
                "articles": all_news[:30],  # Return top 30 articles
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error getting market sentiment news: {e}")
            return {
                "news_count": 0,
                "crypto_news_count": 0,
                "stock_news_count": 0,
                "forex_news_count": 0,
                "news_texts": [],
                "articles": [],
                "timestamp": datetime.now(),
            }

    async def _get_newsapi_articles(
        self, query: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetches articles from NewsAPI.org.

        Args:
            query (str): The search query.
            limit (int): The number of articles to fetch.

        Returns:
            List[Dict[str, Any]]: A list of formatted news articles.
        """
        try:
            # Get articles from the last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.newsapi_client.get_everything(
                    q=query,
                    from_param=from_date,
                    language="en",
                    sort_by="publishedAt",
                    page_size=limit,
                ),
            )

            articles = [
                {
                    "title": article["title"],
                    "description": article["description"],
                    "content": article["content"],
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "published_at": datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    ),
                    "author": article["author"],
                    "image_url": article["urlToImage"],
                }
                for article in response.get("articles", [])
            ]
            return articles

        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []

    async def _get_finnhub_news(
        self, category: str, limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Fetches general news from Finnhub for a specific category.

        Args:
            category (str): The news category (e.g., "general", "forex", "crypto").
            limit (int): The number of articles to return.

        Returns:
            List[Dict[str, Any]]: A list of formatted news articles.
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.finnhub_client.general_news(category, min_id=0)
            )

            articles = [
                {
                    "title": article["headline"],
                    "description": article["summary"],
                    "content": article["summary"],
                    "url": article["url"],
                    "source": article["source"],
                    "published_at": datetime.fromtimestamp(article["datetime"]),
                    "author": None,
                    "image_url": article["image"],
                }
                for article in response[:limit]
            ]
            return articles

        except Exception as e:
            logger.error(f"Finnhub news error: {e}")
            return []

    async def _get_finnhub_company_news(
        self, symbol: str, limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Fetches company-specific news from Finnhub.

        Args:
            symbol (str): The company stock symbol.
            limit (int): The number of articles to return.

        Returns:
            List[Dict[str, Any]]: A list of formatted news articles.
        """
        try:
            # Get news from the last 30 days
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.finnhub_client.company_news(
                    symbol, _from=from_date, to=to_date
                ),
            )

            articles = [
                {
                    "title": article["headline"],
                    "description": article["summary"],
                    "content": article["summary"],
                    "url": article["url"],
                    "source": article["source"],
                    "published_at": datetime.fromtimestamp(article["datetime"]),
                    "author": None,
                    "image_url": article["image"],
                }
                for article in response[:limit]
            ]
            return articles

        except Exception as e:
            logger.error(f"Finnhub company news error: {e}")
            return []

    async def _get_newsdata_articles(
        self, query: str, limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Fetches articles from NewsData.io.

        Args:
            query (str): The search query.
            limit (int): The number of articles to fetch.

        Returns:
            List[Dict[str, Any]]: A list of formatted news articles.
        """
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                "apikey": self.newsdata_key,
                "q": query,
                "language": "en",
                "size": limit,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            articles = [
                {
                    "title": article["title"],
                    "description": article["description"],
                    "content": article["content"],
                    "url": article["link"],
                    "source": article["source_id"],
                    "published_at": datetime.fromisoformat(article["pubDate"]),
                    "author": (
                        article.get("creator", [None])[0]
                        if article.get("creator")
                        else None
                    ),
                    "image_url": article.get("image_url"),
                }
                for article in data.get("results", [])
            ]
            return articles

        except Exception as e:
            logger.error(f"NewsData.io error: {e}")
            return []

    async def _get_alphavantage_news(
        self, symbol: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetches news and sentiment from Alpha Vantage.

        Args:
            symbol (str): The stock symbol to fetch news for.
            limit (int): The number of articles to return.

        Returns:
            List[Dict[str, Any]]: A list of formatted news articles.
        """
        try:
            response, _ = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.alphavantage.get_news_sentiment(tickers=symbol)
            )

            articles = [
                {
                    "title": article["title"],
                    "description": article["summary"],
                    "content": article["summary"],
                    "url": article["url"],
                    "source": article["source"],
                    "published_at": datetime.strptime(
                        article["time_published"], "%Y%m%dT%H%M%S"
                    ),
                    "author": (
                        article.get("authors", [None])[0]
                        if article.get("authors")
                        else None
                    ),
                    "image_url": article.get("banner_image"),
                }
                for article in response.get("feed", [])[:limit]
            ]
            return articles

        except Exception as e:
            logger.error(f"Alpha Vantage news error: {e}")
            return []

    def _remove_duplicates(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Removes duplicate articles based on title similarity.

        Args:
            articles (List[Dict[str, Any]]): A list of article dictionaries.

        Returns:
            List[Dict[str, Any]]: A list of unique articles.
        """
        unique_articles = []
        seen_titles = set()

        for article in articles:
            if article.get("title"):
                title_lower = article["title"].lower()
                # Simple duplicate detection
                if title_lower not in seen_titles:
                    unique_articles.append(article)
                    seen_titles.add(title_lower)

        return unique_articles

    async def _test_newsapi(self):
        """Tests the NewsAPI connection by fetching one headline."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.newsapi_client.get_top_headlines(page_size=1)
            )
            logger.info("NewsAPI connection test successful")
        except Exception as e:
            logger.warning(f"NewsAPI test failed: {e}")

    async def _test_finnhub(self):
        """Tests the Finnhub connection by fetching one general news item."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.finnhub_client.general_news("general", min_id=0)[:1]
            )
            logger.info("Finnhub connection test successful")
        except Exception as e:
            logger.warning(f"Finnhub test failed: {e}")

    async def health_check(self) -> bool:
        """
        Performs a health check on the news service.

        It checks if at least one of the underlying news API clients is responsive.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        try:
            # Test at least one news source
            if self.newsapi_client:
                await self._test_newsapi()
                return True
            if self.finnhub_client:
                await self._test_finnhub()
                return True
            return False
        except Exception as e:
            logger.error(f"News service health check failed: {e}")
            return False

    async def shutdown(self):
        """Shuts down the news service."""
        logger.info("Shutting down news service...")
        self.initialized = False
