from src.domain.ports import FinancialsProvider, UnitOfWork, Logger

class UpdateFinancials:
    def __init__(self, uow_factory: UnitOfWork, financials_provider: FinancialsProvider,logger:Logger):
        self._uow_factory = uow_factory
        self._provider = financials_provider
        self._logger=logger

    async def run(self) -> dict:
        created, skipped = 0, 0

        async with self._uow_factory() as uow:
            tickers = await uow.ticker_repository.get_all_tickers()

        for ticker in tickers:
            async with self._uow_factory() as uow:
                try:
                    financials = await self._provider.get_financials(ticker=ticker)
                    if await uow.financials_repository.check_financials_existence(
                        financials=financials, ticker=ticker
                    ):
                        skipped += 1
                        continue

                    financials=await uow.financials_repository.add_financials(financials)
                    await uow.financials_repository.link_financials_to_ticker(ticker, financials)
                    await uow.commit()
                    self._logger.info(f"{ticker.ticker_name} financials commited")
                    created += 1

                except Exception as e:
                    self._logger.error(f"Error occurred: {e}")
                    continue

        return {"created": created, "skipped": skipped}
