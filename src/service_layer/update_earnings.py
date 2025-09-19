from src.domain.ports import EarningsProvider, UnitOfWork, Logger

class UpdateEarnings:
    def __init__(self, uow_factory: UnitOfWork, earnings_provider: EarningsProvider,logger:Logger):
        self._uow_factory = uow_factory
        self._provider = earnings_provider
        self._logger=logger

    async def run(self) -> dict:
        created, skipped = 0, 0

        async with self._uow_factory() as uow:
            tickers = await uow.ticker_repository.get_all_tickers()

        for ticker in tickers:
            async with self._uow_factory() as uow:
                try:
                    earnings = await self._provider.get_earnings(ticker=ticker)
                    if await uow.earnings_repository.check_earnings_existence(
                        earnings=earnings, ticker=ticker
                    ):
                        skipped += 1
                        continue

                    earnings=await uow.earnings_repository.add_earnings(earnings)
                    await uow.earnings_repository.link_earnings_to_ticker(ticker, earnings)
                    await uow.commit()
                    self._logger.info(f"{ticker.ticker_name} earnings commited")
                    created += 1

                except Exception as e:
                    self._logger.error(f"Error occurred: {e}")
                    continue

        return {"created": created, "skipped": skipped}
