from backend.src.adapters.outbound.neo4j.driver import get_admin_session

async def get_graph_schema():
    nodes_properties={}
    async with await get_admin_session() as session:
        result = await session.run("CALL db.schema.visualization()")
        records = await result.data()
        nodes=records[0]["nodes"]
        relationships=records[0]["relationships"]
        for node in nodes:
            query=f"""
            MATCH (n:{node['name']})
            RETURN DISTINCT keys(n) AS properties
            LIMIT 1;
            """
            result = await session.run(query)
            records = await result.data()
            nodes_properties[node['name']]=records[0]["properties"]

        new_relationships=[]
        for i,rel in enumerate(relationships):
            query=f"""
            MATCH ()-[r:{relationships[i][1]}]->()
            RETURN DISTINCT keys(r) AS properties
            LIMIT 1
            """
            result = await session.run(query)
            records = await result.data()
            new_rel=(relationships[i][0],{"edge_name":relationships[i][1],"properties":records[0]['properties']},relationships[i][2])
            new_relationships.append(new_rel)

        schema=f"Nodes:\n{nodes_properties}\n\nRelationships:\n{new_relationships}"
        return schema

