from jinja2 import Environment, FileSystemLoader
import os
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage,ToolMessage,RemoveMessage
from src.adapters.outbound.llm.google_ai import GoogleGen
import json
from src.domain.models import TickerSupplierRelationship, Ticker
from typing import List
import asyncio
from bs4 import BeautifulSoup
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
current_dir = os.path.dirname(os.path.abspath(__file__))



class Workflow:
    def __init__(self) -> None:
        self.llm_obj = GoogleGen()
        self.llm= self.llm_obj.llm
        self.llm_sleep= self.llm_obj.llm_sleep
        self.embeding_model= GoogleGenerativeAIEmbeddings(model="models/embedding-001",request_options={"output_dimensionality": 768})
    async def parse(self, text: str) -> List[TickerSupplierRelationship]:
        try:
            data = json.loads(text)
            return [TickerSupplierRelationship(
                ticker=d["ticker"],
                sentiment=d["sentiment"],
                justification=d["justification"]
            ) for d in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse LLM output: {e}")
    async def load_prompt(self,template_name, **kwargs):
        env = Environment(loader=FileSystemLoader(os.path.join(current_dir,'prompts', 'templates')))
        template = env.get_template(template_name)
        return template.render(**kwargs)
    
    async def supply_chain_extractor(self,sec_filing: str,ticker: Ticker) -> List[TickerSupplierRelationship]:
        relevant_sections = await self.extract_supply_chain_text(sec_filing)
        prompt = await self.load_prompt("supply_chain_extractor_prompt.jinja",
                                   company_ticker=ticker.ticker_name,
                                   relevant_sections=relevant_sections)
        response = await self.llm.ainvoke(prompt)

        if response.content[0]=="`":
            response.content=response.content[7:-4]
        relationships= await self.parse(text=response.content)
        await asyncio.sleep(self.llm_sleep)
        return relationships
    
    async def extract_supply_chain_text(self,filing_text):
        try:
            soup = BeautifulSoup(filing_text, 'html.parser')
                        
            spans = soup.find_all('span')
            filtered_spans=[]
            for span in spans:
                if len([word for word in span.text.split(' ')])>7:
                    filtered_spans.append(span)
            document_text=""
            for span in filtered_spans:
                document_text+=span.text+'\n'
                text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200,  # small overlap for context
                length_function=len,
                separators=["\n\n", "\n", ".", " ", ""]
                )

            chunks = text_splitter.split_text(document_text)




            chunk_vectors = self.embeding_model.embed_documents(chunks)

            query = (
                "Our company maintains a robust network of suppliers and vendors to ensure a steady flow of materials. "
                "We work closely with manufacturers to optimize production processes and maintain quality standards. "
                "Additionally, our production partners collaborate on joint projects to improve efficiency, while "
                "specialized component providers supply critical parts that are essential for our final products. "
                "This integrated ecosystem allows us to manage risks and maintain a resilient supply chain."
            )

            query_vector = self.embeding_model.embed_query(query)


            def cosine_similarity(a, b):
                a, b = np.array(a), np.array(b)
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            scores = [cosine_similarity(query_vector, vec) for vec in chunk_vectors]
            ranked_chunks = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)


            top_k = 10
            relevant_sections=""
            for i, (chunk, score) in enumerate(ranked_chunks[:top_k], 1):
                relevant_sections+=f"{chunk}\n\n"
            return relevant_sections
            
        except Exception as e:
            return []
