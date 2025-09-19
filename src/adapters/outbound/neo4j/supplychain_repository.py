from src.domain.ports import SupplyChainRepository
from src.domain.models import Ticker, TickerSupplierRelationship
import requests
from typing import List
from sklearn.neighbors import NearestNeighbors
from src.adapters.outbound.logging.std_logger import StdLogger
from neo4j import AsyncTransaction
from dataclasses import asdict
from src.adapters.outbound.neo4j.common_queries import create_node, add_relation, delete_node
from src.adapters.outbound.agents.supplier_relationship.workflow import Workflow






class Neo4jSupplyChainRepository(SupplyChainRepository):
    def __init__(self, tx: AsyncTransaction) -> None:
        self._logger=StdLogger()
        self.tx = tx
        self.embeding_model_deduplication= GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07",request_options={"output_dimensionality": 3072})

    async def get_secfiling(self,ticker: Ticker)-> str:
        headers = {'User-Agent': 'YourApp (your-email@example.com)'}
        form_type: str = "10-K"
        company_url = f"https://www.sec.gov/files/company_tickers.json"
        response = requests.get(company_url, headers=headers)
        companies = response.json()
        
        cik = None
        for company in companies.values():
            if company['ticker'] == ticker.upper():
                cik = str(company['cik_str']).zfill(10)
                break
                
        if not cik:
            return None
            
        filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(filings_url, headers=headers)
        filings_data = response.json()
        
        recent_filings = filings_data['filings']['recent']
        for i, form in enumerate(recent_filings['form']):
            if form == form_type:
                accession = recent_filings['accessionNumber'][i].replace('-', '')
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{recent_filings['accessionNumber'][i]}.txt"
                filing_response = requests.get(filing_url, headers=headers)
                return filing_response.text
                
        return None
    async def extract_date(self, sec_filing: str)-> str:
        sec_filing=sec_filing.split('\n')
        for line in sec_filing:
            if "<ACCEPTANCE-DATETIME>" in line:
                date=line.split("<ACCEPTANCE-DATETIME>")[1]
                break
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
    
        return f"{year}-{month}-{day}"

    async def check_filing_existence(self, ticker:  Ticker, sec_filing_date: str) -> bool:
        query = """
        MATCH (ticker:TICKER)-[rel:HAS_SUPPLIER]->(supplier:SUPPLIER)
        WHERE ticker.ticker_name=$ticker_name and rel.date=$filing_date
        RETURN ticker.ticker_name AS ticker_name
        """
        result = await self.tx.run(query, {"ticker_name": ticker, "filing_date":sec_filing_date})        
        record = await result.single()

        if record:
            return True
        else:
            return False
    async def delete_supply_chains(self,ticker: Ticker) -> str:
        query = """
        MATCH (ticker:TICKER)-[rel:HAS_SUPPLIER]->(supplier:SUPPLIER)
        WHERE ticker.ticker_name=$ticker_name
        DELETE rel
        """
        result = await self.tx.run(query, {"ticker_name": ticker})
        return "Supply chains deleted"
    async def extract_ticker_supplier_relationships(self, sec_filing: str,ticker: Ticker) -> List[TickerSupplierRelationship]:
        workflow=Workflow()
        return await workflow.supply_chain_extractor(sec_filing=sec_filing,ticker=ticker)
    async def add_supplier(self, ticker_supplier_relationship: TickerSupplierRelationship) -> TickerSupplierRelationship:
        props = asdict(ticker_supplier_relationship)
        props.pop("supplier_id", None)
        props["supplier_id"] = await create_node(tx=self.tx, label="NEWS", properties={"supplier_name":props["supplier_name"],"supplier_type":props["supplier_type"]})
        return TickerSupplierRelationship(**props)
    async def link_supplier_to_ticker(self, ticker:Ticker, ticker_supplier_relationship: TickerSupplierRelationship) -> str:
        await add_relation(tx=self.tx,
                        left_label="TICKER",
                        right_label="SUPPLIER",
                        rel_label="HAS_SUPPLIER",
                        left_id=ticker.ticker_id,
                        right_id=ticker_supplier_relationship.supplier_id,
                        properties={"date":ticker_supplier_relationship.date,"risk":ticker_supplier_relationship.risk,"relationship_type":ticker_supplier_relationship.relationship_type,"evidence":ticker_supplier_relationship.evidence,"confidence_score":ticker_supplier_relationship.confidence_score})
        return "HAS_SUPPLIER relation added successfully"                        
    
    async def get_suppliers_by_type(self,supplier_type):
        query= f"""
        MATCH (supplier:SUPPLIER)
        WHERE supplier.supplier_type=$supplier_type
        RETURN supplier.supplier_name AS supplier_name"""

        result = await self.tx.run(query,supplier_type=supplier_type)
        records= await result.data()
        seen = set()
        data = []
        for item in records:
            val = item.get("supplier_name")
            if val not in seen:
                seen.add(val)
                data.append(item)
        return data
    
    async def group_suppliers(self, embeddings,names, threshold=0.9, k=10):
    
        nn = NearestNeighbors(n_neighbors=k, metric="cosine").fit(embeddings)
        sims, idxs = nn.kneighbors(embeddings)
        class UnionFind:
            def __init__(self, n):
                self.parent = list(range(n))
            async def find(self, x):
                while self.parent[x] != x:
                    self.parent[x] = self.parent[self.parent[x]]
                    x = self.parent[x]
                return x
            async def union(self, x, y):
                px, py = self.find(x), self.find(y)
                if px != py:
                    self.parent[py] = px
        uf = UnionFind(len(embeddings))
        for i, (row_idxs, row_sims) in enumerate(zip(idxs, sims)):
            for j, dist in zip(row_idxs, row_sims):
                sim = 1 - dist
                if i != j and sim >= threshold:
                    await uf.union(i, j)
        groups = {}
        for i in range(len(names)):
            root = await uf.find(i)
            groups.setdefault(root, []).append(names[i])

        return list(groups.values())

    async def get_ticker_n_supplier(self,tx, supplier_names,supplier_type):
        query= f"""
        MATCH (ticker:TICKER)-[rel:HAS_SUPPLIER]->(supplier:SUPPLIER)
        WHERE supplier.supplier_name in $supplier_names AND supplier.supplier_type=$supplier_type
        RETURN ticker.id AS ticker_id, supplier.id AS supplier_id, properties(rel) AS relationship_properties;
        """

        result = await tx.run(query, supplier_names=supplier_names,supplier_type=supplier_type)
        records= await result.data()
        return records
    async def redirect_tickers_to_suppliers(self,groups,supplier_type):
        
        for group in groups:
            parent=group[0]
            parent_id= await create_node(tx=self.tx,label="SUPPLIER",properties={"supplier_name": parent,"supplier_type": supplier_type})
            ticker_n_suppliers= await self.get_ticker_n_supplier(self.tx, group,supplier_type)
            for i in range(len(ticker_n_suppliers)):
                await add_relation(tx=self.tx,
                                    left_label="TICKER",
                                    right_label="SUPPLIER",
                                    rel_label="HAS_SUPPLIER",
                                    left_id=ticker_n_suppliers[i]["ticker_id"],
                                    right_id=parent_id,
                                    properties=ticker_n_suppliers[i]["relationship_properties"])
                
                await delete_node(tx=self.tx,label="SUPPLIER",id=ticker_n_suppliers[i]["supplier_id"])
    
    async def supplier_deduplication(self) -> str:
        supplier_companies= await self.get_suppliers_by_type("company")
        supplier_countries= await self.get_suppliers_by_type("country")
        supplier_regions= await self.get_suppliers_by_type("region")
        company_names = [s["supplier_name"] for s in supplier_companies]
        companies_embeddings = self.embeding_model_deduplication.embed_documents(company_names)

        country_names = [s["supplier_name"] for s in supplier_countries]
        countries_embeddings = self.embeding_model_deduplication.embed_documents(country_names)

        region_names = [s["supplier_name"] for s in supplier_regions]
        regions_embeddings = self.embeding_model_deduplication.embed_documents(region_names) 



        company_groups = []
        if company_names:
            company_groups = await self.group_suppliers(embeddings=companies_embeddings, names=company_names)
        country_groups = []
        if country_names:
            country_groups = await self.group_suppliers(embeddings=countries_embeddings, names=country_names)
        region_groups = []
        if region_names:
            region_groups = await self.group_suppliers(embeddings=regions_embeddings, names=region_names)


        await self.redirect_tickers_to_suppliers(groups=company_groups,supplier_type="company")
        await self.redirect_tickers_to_suppliers(groups=country_groups,supplier_type="country")
        await self.redirect_tickers_to_suppliers(groups=region_groups,supplier_type="region")