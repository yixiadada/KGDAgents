from neo4j import GraphDatabase

# 配置连接信息
uri = ""  # 替换为你的Neo4j地址
username = ""  # 替换为你的用户名
password = ""  # 替换为你的密码
driver = GraphDatabase.driver(uri, auth=(username, password))

# 查询函数
def fetch_diseases_for_symptom(symptom_name):
    query = """
    MATCH (s:Symptom {name: $symptom_name})<-[:HAS_SYMPTOM]-(d:Disease)
    RETURN d.name AS Disease
    """
    with driver.session() as session:
        result = session.run(query, symptom_name=symptom_name)
        # 提取结果
        diseases = [record["Disease"] for record in result]
        return diseases


