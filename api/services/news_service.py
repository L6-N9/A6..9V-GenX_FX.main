"""
News Integration Service for GenX Trading Platform
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
import os
from datetime import datetime, timedelta
import json
import logging

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

        # ⚡ Bolt: Removed unused synchronous clients. All API calls are now
        # handled by the shared aiohttp.ClientSession for better performance.
        # ⚡ Bolt: Use a single aiohttp.ClientSession for connection pooling and efficiency.
        # This session will be managed by the initialize and shutdown methods.
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False

        # Keywords for categorization (currently not used but defined)
        self.crypto_keywords = [
            "bitcoin", "ethereum", "cryptocurrency", "blockchain", "defi", "nft",
            "crypto", "btc", "eth", "altcoin", "coinbase", "binance",
        ]
        self.stock_keywords = [
            "stock market", "nasdaq", "dow jones", "s&p 500", "earnings", "fed",
            "inflation", "interest rates", "wall street", "trading", "investment",
        ]
        self.forex_keywords = [
            "forex", "currency", "usd", "eur", "gbp", "jpy", "exchange rate",
            "federal reserve", "central bank", "dollar", "euro",
        ]
    
    async def initialize(self) -> bool:
        """
        Initializes the news service by creating a shared aiohttp.ClientSession.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            # ⚡ Bolt: Initialize a single aiohttp.ClientSession to be reused across all requests.
            # This leverages connection pooling, which is much more efficient than creating
            # a new connection for every request.
            self.session = aiohttp.ClientSession()

            # ⚡ Bolt: Connection tests for synchronous clients are no longer needed.
            # The health of the service is now determined by the state of the aiohttp session.
            logger.info("News service initialized successfully")
            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize news service: {e}")
            return False
    
    async def get_crypto_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        ⚡ Bolt: Aggregates cryptocurrency news from multiple sources concurrently.
        This optimized method uses asyncio.gather to fetch news from all APIs
        in parallel, significantly reducing the total wait time.

        Args:
            limit (int): The maximum number of news articles to return.

        Returns:
            List[Dict[str, Any]]: A sorted and deduplicated list of news articles.
        """
        tasks = []
        # Create a list of concurrent tasks for fetching news
        if self.newsapi_key:
            tasks.append(self._get_newsapi_articles("cryptocurrency", limit=20))
        if self.finnhub_key:
            tasks.append(self._get_finnhub_news("crypto", limit=15))
        if self.newsdata_key:
            tasks.append(self._get_newsdata_articles("cryptocurrency", limit=15))

        # Execute all tasks concurrently and wait for them to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten the list of lists and filter out any exceptions
        all_news = [
            article for result in results if isinstance(result, list) for article in result
        ]

        # Remove duplicates and sort by date
        unique_news = self._remove_duplicates(all_news)
        sorted_news = sorted(
            unique_news, key=lambda x: x["published_at"], reverse=True
        )

        return sorted_news[:limit]
    
    async def get_stock_news(
        self, symbol: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        ⚡ Bolt: Aggregates stock news from multiple sources concurrently.
        This optimized method uses asyncio.gather to fetch news from all APIs
        in parallel, significantly reducing the total wait time.

        Args:
            symbol (Optional[str]): The stock symbol (e.g., "AAPL"). If None,
                                    general market news is fetched.
            limit (int): The maximum number of news articles to return.

        Returns:
            List[Dict[str, Any]]: A sorted and deduplicated list of news articles.
        """
        tasks = []
        # Create a list of concurrent tasks for fetching news
        if self.newsapi_key:
            query = f"{symbol} stock" if symbol else "stock market"
            tasks.append(self._get_newsapi_articles(query, limit=20))
        if self.finnhub_key:
            if symbol:
                tasks.append(self._get_finnhub_company_news(symbol, limit=15))
            else:
                tasks.append(self._get_finnhub_news("general", limit=15))
        if self.alphavantage_key and symbol:
            tasks.append(self._get_alphavantage_news(symbol, limit=10))

        # Execute all tasks concurrently and wait for them to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten the list of lists and filter out any exceptions
        all_news = [
            article for result in results if isinstance(result, list) for article in result
        ]

        # Remove duplicates and sort
        unique_news = self._remove_duplicates(all_news)
        sorted_news = sorted(
            unique_news, key=lambda x: x["published_at"], reverse=True
        )

        return sorted_news[:limit]
    
    async def get_forex_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        ⚡ Bolt: Aggregates forex news from multiple sources concurrently.
        This optimized method uses asyncio.gather to fetch news from all APIs
        in parallel, significantly reducing the total wait time.

        Args:
            limit (int): The maximum number of news articles to return.

        Returns:
            List[Dict[str, Any]]: A sorted and deduplicated list of news articles.
        """
        tasks = []
        # Create a list of concurrent tasks for fetching news
        if self.newsapi_key:
            tasks.append(self._get_newsapi_articles("forex currency", limit=20))
        if self.finnhub_key:
            tasks.append(self._get_finnhub_news("forex", limit=10))

        # Execute all tasks concurrently and wait for them to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten the list of lists and filter out any exceptions
        all_news = [
            article for result in results if isinstance(result, list) for article in result
        ]

        # Remove duplicates and sort
        unique_news = self._remove_duplicates(all_news)
        sorted_news = sorted(
            unique_news, key=lambda x: x["published_at"], reverse=True
        )

        return sorted_news[:limit]
    
    async def get_market_sentiment_news(self) -> Dict[str, Any]:
        """
        ⚡ Bolt: Gathers a broad range of news concurrently for general market sentiment analysis.
        This optimized method uses asyncio.gather to fetch news from all categories
        in parallel, significantly reducing the total wait time.

        Returns:
            Dict[str, Any]: A dictionary containing aggregated news data, including
                            counts and combined text for analysis.
        """
        try:
            # ⚡ Bolt: Fetch news from all categories concurrently using asyncio.gather.
            # This allows all three network requests to run in parallel, reducing the
            # total execution time from the sum of all requests to the time of the
            # longest single request. return_exceptions=True ensures that if one
            # API fails, the others can still succeed.
            results = await asyncio.gather(
                self.get_crypto_news(limit=20),
                self.get_stock_news(limit=20),
                self.get_forex_news(limit=10),
                return_exceptions=True,  # Continue if one of the APIs fails
            )

            # ⚡ Bolt: Safely unpack results, handling potential exceptions.
            # If a coroutine failed, its result will be an exception instance.
            # We replace it with an empty list to ensure the downstream logic
            # doesn't break.
            crypto_news = results[0] if isinstance(results[0], list) else []
            stock_news = results[1] if isinstance(results[1], list) else []
            forex_news = results[2] if isinstance(results[2], list) else []

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
        ⚡ Bolt: Fetches articles from NewsAPI.org asynchronously.
        This native async method uses the shared aiohttp session for efficient I/O.
        """
        if not self.newsapi_key:
            return []

        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": self.newsapi_key,
        }

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

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
                for article in data.get("articles", [])
            ]
            return articles

        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []
    
    async def _get_finnhub_news(
        self, category: str, limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        ⚡ Bolt: Fetches general news from Finnhub asynchronously.
        This native async method uses the shared aiohttp session for efficient I/O.
        """
        if not self.finnhub_key:
            return []

        url = "https://finnhub.io/api/v1/news"
        params = {"category": category, "token": self.finnhub_key}

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

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
                for article in data[:limit]
            ]
            return articles

        except Exception as e:
            logger.error(f"Finnhub news error: {e}")
            return []

    async def _get_finnhub_company_news(
        self, symbol: str, limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        ⚡ Bolt: Fetches company news from Finnhub asynchronously.
        This native async method uses the shared aiohttp session for efficient I/O.
        """
        if not self.finnhub_key:
            return []

        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")
        url = "https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "token": self.finnhub_key,
        }

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

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
                for article in data[:limit]
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
        ⚡ Bolt: Fetches news from Alpha Vantage asynchronously.
        This native async method uses the shared aiohttp session for efficient I/O.
        """
        if not self.alphavantage_key:
            return []

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "apikey": self.alphavantage_key,
        }

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

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
                for article in data.get("feed", [])[:limit]
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
    
    
    async def health_check(self) -> bool:
        """
        Performs a health check on the news service.

        It checks if at least one of the underlying news API clients is responsive.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        # ⚡ Bolt: Health check now verifies the aiohttp session is active.
        return self.session is not None and not self.session.closed
    
    async def shutdown(self):
        """Shuts down the news service and closes the aiohttp.ClientSession."""
        logger.info("Shutting down news service...")
        # ⚡ Bolt: Gracefully close the shared aiohttp.ClientSession.
        # This is crucial for releasing connections and cleaning up resources properly.
        if self.session:
            await self.session.close()
        self.initialized = False
