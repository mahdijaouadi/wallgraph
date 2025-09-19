from src.domain.ports import UnitOfWork, Logger

class UpdateSupplyChain:
    def __init__(self, uow_factory: UnitOfWork, logger:Logger):
        self._uow_factory = uow_factory
        self._logger=logger

    async def run(self) -> dict:
        created, skipped = 0, 0

        async with self._uow_factory() as uow:
            tickers = await uow.ticker_repository.get_all_tickers()

        for i in range(306,len(tickers)):
            ticker=tickers[i]
            self._logger.info(f"ticker: {ticker}, number {i}")
            async with self._uow_factory() as uow:
                try:
                    sec_filing = await uow.supplychain_repository.get_secfiling(ticker=ticker)
                    if not sec_filing:
                        skipped+=1
                        continue
                    sec_filing_date= await uow.supplychain_repository.extract_date(sec_filing)
                    if await uow.supplychain_repository.check_filing_existence(ticker=ticker,sec_filing_date=sec_filing_date):
                        skipped += 1
                        continue
                    await uow.supplychain_repository.delete_supply_chains(ticker=ticker)
                    ticker_supplier_relationships=await uow.supplychain_repository.extract_ticker_supplier_relationships(sec_filing=sec_filing,ticker=ticker)
                    for ticker_supplier_relationship in ticker_supplier_relationships:
                        ticker_supplier_relationship.date=sec_filing_date
                        ticker_supplier_relationship= await uow.supplychain_repository.add_supplier(ticker_supplier_relationship)
                        await uow.supplychain_repository.link_supplier_to_ticker(ticker, ticker_supplier_relationship)
                        
                    await uow.commit()

                    self._logger.info(f"{ticker.ticker_name} suppliers commited")
                    created += 1

                except Exception as e:
                    self._logger.error(f"Error occurred: {e}")
                    continue
        async with self._uow_factory() as uow:
            await uow.supplychain_repository.supplier_deduplication()
            await uow.commit()

        return {"created": created, "skipped": skipped}
