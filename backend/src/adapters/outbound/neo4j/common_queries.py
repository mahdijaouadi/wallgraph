import uuid
import re
async def add_relation(tx, left_label, right_label, rel_label, left_id, right_id, properties={}):

    query = f"""
    MATCH (left:{left_label} {{id: $left_id}}), (right:{right_label} {{id: $right_id}})
    MERGE (left)-[r:{rel_label}]->(right)
    SET r += $rel_props
    RETURN r
    """

    rel_props = properties  # remaining properties go to the relationship
    result = await tx.run(query, {"left_id": left_id, "right_id": right_id, "rel_props": rel_props})
    return result


def sanitize_key(key: str) -> str:
    # Replace spaces and special characters with underscores for parameters
    return re.sub(r'[^a-zA-Z0-9_]', '_', key)

async def create_node(tx, label, properties):
    id = str(uuid.uuid4())
    properties = {"id": id, **properties}

    # Build a map of {sanitized_key: value}
    sanitized_props = {sanitize_key(k): v for k, v in properties.items()}

    # Build SET clause using original key for Neo4j, sanitized key for params
    set_clause = ", ".join([f"n.`{k}` = ${sanitize_key(k)}" for k in properties.keys()])

    query = f"""
    MERGE (n:{label} {{id: $id}})
    SET {set_clause}
    """

    await tx.run(query, {"id": id, **sanitized_props})
    return id




async def delete_node(tx, label, id):

    query = f"""
    MATCH (n:{label} {{id: $id}})
    DETACH DELETE n
    """

    await tx.run(query, {"id": id})
    return id

