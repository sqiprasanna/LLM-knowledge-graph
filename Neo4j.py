from neo4j import GraphDatabase
import sqlite3

class Neo4jManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_data_from_sqlite(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT user_id, entity1, entity2, type, relation, sentiment, brand, category, sub_category
        FROM processed_reviews
        ''')

        rows = cursor.fetchall()

        with self.driver.session() as session:
            for row in rows:
                user_id, entity1, entity2, type_, relation, sentiment, brand, category, sub_category = row
                session.write_transaction(self._create_graph, user_id, entity1, entity2, type_, relation, sentiment, brand, category, sub_category)

        conn.close()

    @staticmethod
    def _create_graph(tx, user_id, entity1, entity2, type_, relation, sentiment, brand, category, sub_category):
        tx.run('''
        MERGE (e1:Entity {name: $entity1, type: $type_, sentiment: $sentiment, brand: $brand, category: $category, sub_category: $sub_category})
        MERGE (e2:Entity {name: $entity2, type: $type_, sentiment: $sentiment, brand: $brand, category: $category, sub_category: $sub_category})
        MERGE (e1)-[:RELATED {relation: $relation, user_id: $user_id}]->(e2)
        ''', entity1=entity1, entity2=entity2, type_=type_, relation=relation, sentiment=sentiment, brand=brand, category=category, sub_category=sub_category, user_id=user_id)

# Example usage with cloud-hosted Neo4j instance
neo4j_manager = Neo4jManager(uri="neo4j+s://67d73379.databases.neo4j.io", user="neo4j", password="6BHbWlXEUuwFIOy69qxSg1yYo-A_dQd_NzYcpd-nxdY")
neo4j_manager.load_data_from_sqlite(db_path="amazon_reviews.db")
neo4j_manager.close()




def find_frequently_copurchased_items(session):
    query = '''
    MATCH (e1:Entity)-[r:RELATED {relation: 'Frequently Co-Purchased'}]->(e2:Entity)
    RETURN e1.name AS Entity1, e2.name AS Entity2, COUNT(r) AS Frequency
    ORDER BY Frequency DESC
    LIMIT 5
    '''
    result = session.run(query)
    for record in result:
        print(record["Entity1"], "and", record["Entity2"], "were co-purchased", record["Frequency"], "times")

# Example usage
with neo4j_manager.driver.session() as session:
    find_frequently_copurchased_items(session)
def predict_customer_preferences(session, user_id):
    query = '''
    MATCH (u:Entity {name: $user_id})-[r:RELATED]->(e:Entity)
    RETURN e.name AS PreferredEntity, COUNT(r) AS PreferenceScore
    ORDER BY PreferenceScore DESC
    LIMIT 5
    '''
    result = session.run(query, user_id=user_id)
    for record in result:
        print("User", user_id, "prefers", record["PreferredEntity"], "with a score of", record["PreferenceScore"])

# Example usage
with neo4j_manager.driver.session() as session:
    predict_customer_preferences(session, user_id='example_user_id')


def detect_sentiment_trends(session):
    query = '''
    MATCH (e:Entity)
    RETURN e.sentiment AS Sentiment, COUNT(e) AS Count
    ORDER BY Count DESC
    '''
    result = session.run(query)
    for record in result:
        print("Sentiment:", record["Sentiment"], "Count:", record["Count"])

# Example usage
with neo4j_manager.driver.session() as session:
    detect_sentiment_trends(session)
