from backend.src.domain.models import Ticker, News, NewsSentiment
from backend.src.domain.ports import NewsRepository
from neo4j import AsyncTransaction
from typing import List
import re
import cloudscraper
from bs4 import BeautifulSoup
from backend.src.adapters.outbound.logging.std_logger import StdLogger
from datetime import datetime, timedelta
from backend.src.adapters.outbound.neo4j.common_queries import create_node, add_relation
from dataclasses import asdict
from backend.src.adapters.outbound.agents.news_sentiment.workflow import Workflow


class GeneralNewsRepository(NewsRepository):
    def __init__(self, tx: AsyncTransaction) -> None:
        self._logger=StdLogger()
        self.tx = tx
    async def scrap_feed(self,url):
        scraper = cloudscraper.create_scraper()

        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_element = soup.find(id="article")
        if next_data_element:
            text=next_data_element.text
            text=text.strip()
            return text
        else:
            "No News, Skip"
    async def similarity_overlap(self, first_feed, second_feed):
        # Normalize: lowercase, remove punctuation
        if not first_feed or not second_feed:
            return 0.0
        def tokenize(text):
            return set(re.findall(r"\w+", text.lower()))
        
        first_set = tokenize(first_feed)
        second_set = tokenize(second_feed)
        
        if not first_set or not second_set:
            return 0.0
        return len(first_set & second_set) / len(first_set | second_set)
    async def get_news(self) -> List[News]:
        url = "https://www.investing.com/news/stock-market-news"
        scraper = cloudscraper.create_scraper()
        now = datetime.now()
        date = now.date()

        response = scraper.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        next_data_element = soup.find(id="__next")
        feeds=[]
        if next_data_element:
            links = [a['href'] for a in next_data_element.find_all('a', href=True)]
            for link in links:
                if 'https://www.investing.com/news/stock-market-news' in link and '#comments' not in link:
                    try:
                        feeds.append(News(news_id= "*", date=date.strftime("%Y-%m-%d"), feed= await self.scrap_feed(url=link)))
                    except Exception as e:
                        self._logger.info(f"Error occured {e}")
                        continue
        return feeds
    async def check_feed_existence(self, news: News) -> bool:
        past_2_days=(datetime.strptime(news.date, "%Y-%m-%d")- timedelta(days=2)).strftime("%Y-%m-%d")
        query = """
        MATCH (news:NEWS)
        WHERE news.date >= $date
        RETURN news.feed AS news_feed
        """
        result = await self.tx.run(query, {"feed": news.feed, "date": past_2_days})
        records = await result.data()
        
        for record in records:
            if await self.similarity_overlap(news.feed, record["news_feed"]) > 0.8:
                return True
        return False
    async def add_news(self, news:News) -> News:
        props = asdict(news)
        props.pop("news_id", None)
        props["news_id"] = await create_node(tx=self.tx, label="NEWS", properties=props)
        return News(**props)
    async def get_news_and_sentiment(self, news:News) -> List[NewsSentiment]:
        workflow=Workflow()
        return await workflow.news_to_ticker_sentiment(news=news)
    async def link_news_to_ticker(self, ticker: Ticker, news: News, news_sentiment: NewsSentiment) -> str:
        await add_relation(tx=self.tx,
                        left_label="NEWS",
                        right_label="TICKER",
                        rel_label="MENTIONED_TICKER",
                        left_id=news.news_id,
                        right_id=ticker.ticker_id,
                        properties={
                                    "sentiment": news_sentiment.sentiment,
                                    "justification": news_sentiment.justification
                                    })
        return "MENTIONED_TICKER relation added successfully"