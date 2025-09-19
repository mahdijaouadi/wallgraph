from backend.src.domain.ports import UnitOfWork, Logger

class UpdateNews:
    def __init__(self, uow_factory: UnitOfWork,logger:Logger):
        self._uow_factory = uow_factory
        self._logger=logger

    async def run(self) -> dict:
        created, skipped = 0, 0
        async with self._uow_factory() as uow:
            tickers = await uow.ticker_repository.get_all_tickers()
            news_list= await uow.news_repository.get_news()
        all_ticker_names= [t.ticker_name for t in tickers]
        self._logger.info(f"Number of news {len(news_list)}")
        for news in news_list:
            async with self._uow_factory() as uow:
                if await uow.news_repository.check_feed_existence(news=news):
                        skipped += 1
                        continue
                news= await uow.news_repository.add_news(news)
                news_and_sentiment_list= await uow.news_repository.get_news_and_sentiment(news)
                for item in news_and_sentiment_list:
                    if item.ticker in all_ticker_names:
                        ticker=[ t for t in tickers if t.ticker_name == item.ticker][0]
                        await uow.news_repository.link_news_to_ticker(ticker, news, item)
                
                await uow.commit()
                self._logger.info(f"news commited")
                created+=1
        return {"created": created, "skipped": skipped}