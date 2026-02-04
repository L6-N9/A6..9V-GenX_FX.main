"""
Reddit Integration Service for GenX Trading Platform
"""

import asyncio
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import praw

logger = logging.getLogger(__name__)


class RedditService:
    """
    A service for fetching and analyzing data from Reddit.

    This service uses the PRAW library to connect to the Reddit API and
    provides methods to get trending posts and analyze sentiment from
    various trading-related subreddits.

    Attributes:
        reddit: The PRAW Reddit instance.
        initialized (bool): True if the service is initialized.
        trading_subreddits (List[str]): A list of subreddits to monitor.
    """

    def __init__(self):
        """
        Initializes the RedditService.

        Retrieves credentials from environment variables and sets up keyword lists.

        Raises:
            ValueError: If Reddit credentials are not properly configured.
        """
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "GenX-Trading-Bot/1.0")

        if not all([self.client_id, self.client_secret, self.username, self.password]):
            raise ValueError("Reddit credentials are not properly configured")

        self.reddit: Optional[praw.Reddit] = None
        self.initialized = False

        # Trading-related subreddits
        self.trading_subreddits = [
            "wallstreetbets",
            "investing",
            "stocks",
            "cryptocurrency",
            "Bitcoin",
            "ethereum",
            "CryptoMarkets",
            "SecurityAnalysis",
            "ValueInvesting",
            "options",
            "Forex",
            "pennystocks",
        ]

        # Keywords for filtering relevant posts
        self.crypto_keywords = [
            "bitcoin",
            "btc",
            "ethereum",
            "eth",
            "crypto",
            "blockchain",
            "defi",
            "nft",
            "altcoin",
            "hodl",
            "moon",
            "dip",
            "pump",
            "dump",
        ]

        self.stock_keywords = [
            "spy",
            "qqq",
            "tsla",
            "aapl",
            "msft",
            "nvda",
            "earnings",
            "bull",
            "bear",
            "calls",
            "puts",
            "options",
            "squeeze",
        ]

    async def initialize(self) -> bool:
        """
        Initializes the Reddit API connection using PRAW.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            loop = asyncio.get_event_loop()
            self.reddit = await loop.run_in_executor(
                None,
                lambda: praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    username=self.username,
                    password=self.password,
                    user_agent=self.user_agent,
                ),
            )

            # Test connection by fetching current user information
            await loop.run_in_executor(None, lambda: self.reddit.user.me())

            logger.info("Reddit service initialized successfully")
            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Reddit service: {e}")
            return False

    async def get_trending_posts(
        self, subreddit_name: str, limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Gets trending (hot) posts from a specified subreddit.

        Args:
            subreddit_name (str): The name of the subreddit.
            limit (int): The maximum number of posts to fetch.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a post.
        """
        if not self.initialized:
            raise ConnectionError("Reddit service is not initialized.")
        try:
            subreddit = await asyncio.get_event_loop().run_in_executor(
                None, self.reddit.subreddit, subreddit_name
            )
            hot_posts = await asyncio.get_event_loop().run_in_executor(
                None, lambda: list(subreddit.hot(limit=limit))
            )

            posts = [
                {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "created_utc": datetime.fromtimestamp(post.created_utc),
                    "author": str(post.author) if post.author else "deleted",
                    "subreddit": post.subreddit.display_name,
                    "url": post.url,
                    "flair": post.link_flair_text,
                    "awards": post.total_awards_received,
                }
                for post in hot_posts
            ]
            return posts

        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []

    async def get_crypto_sentiment(self) -> Dict[str, Any]:
        """
        Aggregates and analyzes sentiment for cryptocurrency-related subreddits.

        Returns:
            Dict[str, Any]: A dictionary summarizing the crypto sentiment.
        """
        try:
            crypto_subreddits = [
                "cryptocurrency",
                "Bitcoin",
                "ethereum",
                "CryptoMarkets",
            ]
            tasks = [
                self.get_trending_posts(sub, limit=10) for sub in crypto_subreddits
            ]
            results = await asyncio.gather(*tasks)
            all_posts = [post for result in results for post in result]

            # Filter for crypto-related posts
            crypto_posts = self._filter_posts_by_keywords(
                all_posts, self.crypto_keywords
            )

            # Analyze sentiment
            sentiment_data = self._analyze_post_sentiment(crypto_posts)

            return {
                "sentiment_score": sentiment_data["sentiment_score"],
                "post_count": len(crypto_posts),
                "avg_score": sentiment_data["avg_score"],
                "trending_topics": sentiment_data["trending_topics"],
                "top_posts": crypto_posts[:5],
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error getting crypto sentiment: {e}")
            return {
                "sentiment_score": 0,
                "post_count": 0,
                "avg_score": 0,
                "trending_topics": [],
                "top_posts": [],
                "timestamp": datetime.now(),
            }

    async def get_stock_sentiment(self) -> Dict[str, Any]:
        """
        Aggregates and analyzes sentiment for stock market-related subreddits.

        Returns:
            Dict[str, Any]: A dictionary summarizing the stock market sentiment.
        """
        try:
            stock_subreddits = [
                "wallstreetbets",
                "investing",
                "stocks",
                "SecurityAnalysis",
            ]
            tasks = [self.get_trending_posts(sub, limit=10) for sub in stock_subreddits]
            results = await asyncio.gather(*tasks)
            all_posts = [post for result in results for post in result]

            # Filter for stock-related posts
            stock_posts = self._filter_posts_by_keywords(all_posts, self.stock_keywords)

            # Analyze sentiment
            sentiment_data = self._analyze_post_sentiment(stock_posts)

            return {
                "sentiment_score": sentiment_data["sentiment_score"],
                "post_count": len(stock_posts),
                "avg_score": sentiment_data["avg_score"],
                "trending_topics": sentiment_data["trending_topics"],
                "top_posts": stock_posts[:5],
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error getting stock sentiment: {e}")
            return {
                "sentiment_score": 0,
                "post_count": 0,
                "avg_score": 0,
                "trending_topics": [],
                "top_posts": [],
                "timestamp": datetime.now(),
            }

    async def get_wallstreetbets_sentiment(self) -> Dict[str, Any]:
        """
        Performs a specific analysis of the r/wallstreetbets subreddit.

        This includes sentiment analysis, trending ticker extraction, and counting
        common emojis.

        Returns:
            Dict[str, Any]: A dictionary summarizing the WSB sentiment.
        """
        try:
            posts = await self.get_trending_posts("wallstreetbets", limit=50)

            # Extract ticker mentions
            tickers = self._extract_tickers(posts)

            # Analyze sentiment
            sentiment_data = self._analyze_post_sentiment(posts)

            return {
                "sentiment_score": sentiment_data["sentiment_score"],
                "trending_tickers": tickers,
                "post_count": len(posts),
                "avg_score": sentiment_data["avg_score"],
                "rocket_count": self._count_emojis(posts, "🚀"),
                "diamond_hands_count": self._count_emojis(posts, "💎"),
                "top_posts": posts[:5],
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error getting WSB sentiment: {e}")
            return {
                "sentiment_score": 0,
                "trending_tickers": {},
                "post_count": 0,
                "avg_score": 0,
                "rocket_count": 0,
                "diamond_hands_count": 0,
                "top_posts": [],
                "timestamp": datetime.now(),
            }

    def _filter_posts_by_keywords(
        self, posts: List[Dict[str, Any]], keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filters a list of posts based on a list of keywords.

        Args:
            posts (List[Dict[str, Any]]): The posts to filter.
            keywords (List[str]): The keywords to search for in post titles and text.

        Returns:
            List[Dict[str, Any]]: A list of posts that contain any of the keywords.
        """
        filtered_posts = []

        for post in posts:
            text = f"{post['title']} {post['selftext']}".lower()

            if any(keyword in text for keyword in keywords):
                filtered_posts.append(post)

        return filtered_posts

    def _analyze_post_sentiment(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs a simple sentiment analysis on a list of posts.

        The sentiment is based on the post's score and upvote ratio.

        Args:
            posts (List[Dict[str, Any]]): The list of posts to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing the sentiment score, average
                            score, and trending topics.
        """
        if not posts:
            return {"sentiment_score": 0, "avg_score": 0, "trending_topics": []}

        # Simple sentiment based on score and upvote ratio
        total_sentiment = 0
        total_score = 0

        for post in posts:
            # Calculate sentiment based on score and upvote ratio
            score_weight = min(post["score"], 1000) / 1000  # Normalize score
            ratio_weight = post["upvote_ratio"]

            post_sentiment = (score_weight + ratio_weight) / 2
            total_sentiment += post_sentiment
            total_score += post["score"]

        avg_sentiment = total_sentiment / len(posts)
        avg_score = total_score / len(posts)

        # Extract trending topics (simplified)
        trending_topics = self._extract_trending_topics(posts)

        return {
            "sentiment_score": avg_sentiment,
            "avg_score": avg_score,
            "trending_topics": trending_topics,
        }

    def _extract_tickers(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extracts potential stock tickers from a list of posts.

        Args:
            posts (List[Dict[str, Any]]): The posts to analyze.

        Returns:
            Dict[str, int]: A dictionary mapping tickers to their mention frequency.
        """
        ticker_pattern = r"\b[A-Z]{2,5}\b"
        ticker_counts: Dict[str, int] = {}

        # Common words to exclude to reduce false positives
        exclude_words = {
            "THE",
            "AND",
            "FOR",
            "ARE",
            "BUT",
            "NOT",
            "YOU",
            "ALL",
            "CAN",
            "HER",
            "WAS",
            "ONE",
            "OUR",
            "HAD",
            "HAS",
            "HAVE",
            "HIS",
            "HOW",
            "ITS",
            "MAY",
            "NEW",
            "NOW",
            "OLD",
            "SEE",
            "TWO",
            "WAY",
            "WHO",
            "BOY",
            "DID",
            "GET",
            "HIM",
            "OWN",
            "SAY",
            "SHE",
            "TOO",
            "USE",
            "WSB",
            "CEO",
            "IPO",
            "SEC",
            "FDA",
            "USA",
            "ETF",
            "YOLO",
        }

        for post in posts:
            text = f"{post['title']} {post['selftext']}"
            tickers = re.findall(ticker_pattern, text)

            for ticker in tickers:
                if ticker not in exclude_words and len(ticker) <= 5:
                    ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        # Sort by frequency and return top 10
        sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_tickers[:10])

    def _extract_trending_topics(self, posts: List[Dict[str, Any]]) -> List[str]:
        """
        Performs a simple keyword extraction to find trending topics.

        Args:
            posts (List[Dict[str, Any]]): The posts to analyze.

        Returns:
            List[str]: A list of the top 5 trending keywords.
        """
        keywords: Dict[str, int] = {}

        for post in posts:
            words = post["title"].lower().split()
            for word in words:
                if len(word) > 3:  # Skip short, common words
                    keywords[word] = keywords.get(word, 0) + 1

        # Sort by frequency and return top 5
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:5]]

    def _count_emojis(self, posts: List[Dict[str, Any]], emoji: str) -> int:
        """
        Counts the occurrences of a specific emoji in the posts.

        Args:
            posts (List[Dict[str, Any]]): The posts to search through.
            emoji (str): The emoji character to count.

        Returns:
            int: The total count of the emoji.
        """
        count = 0
        for post in posts:
            text = f"{post['title']} {post['selftext']}"
            count += text.count(emoji)
        return count

    async def health_check(self) -> bool:
        """
        Checks if the Reddit service is healthy and responsive.

        Returns:
            bool: True if the service is initialized and can connect, False otherwise.
        """
        try:
            if not self.initialized:
                return False

            # Test by getting current user info
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.reddit.user.me()
            )
            return True

        except Exception as e:
            logger.error(f"Reddit health check failed: {e}")
            return False

    async def shutdown(self):
        """Shuts down the Reddit service."""
        logger.info("Shutting down Reddit service...")
        self.initialized = False
