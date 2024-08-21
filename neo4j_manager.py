from neo4j import GraphDatabase
import sqlite3

class Neo4jManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_data_from_sqlite(self, db_path):
        conn = sqlite3.connect(db_path,check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT user_id, entity1, entity2, type, relation, sentiment, brand, category, sub_category, cleaned_review_content, rating
        FROM processed_reviews
        ''')

        rows = cursor.fetchall()

        with self.driver.session() as session:
            for row in rows:
                user_id, entity1, entity2, type_, relation, sentiment, brand, category, sub_category, cleaned_review_content, rating = row
                session.write_transaction(self._create_graph, user_id, entity1, entity2, type_, relation, sentiment, brand, category, sub_category, cleaned_review_content, rating)

        conn.close()

    @staticmethod
    def _create_graph(tx, user_id, entity1, entity2, type_, relation, sentiment, brand, category, sub_category, cleaned_review_content, rating):
        sub_category = sub_category if sub_category else "Unknown"
        
        tx.run('''
        MERGE (c:Community {name: $category})
        MERGE (sc:SubCommunity {name: $sub_category})-[:PART_OF]->(c)
        MERGE (e1:Entity {name: $entity1, type: $type_, sentiment: $sentiment, brand: $brand, category: $category, sub_category: $sub_category})-[:BELONGS_TO]->(sc)
        MERGE (e2:Entity {name: $entity2, type: $type_, sentiment: $sentiment, brand: $brand, category: $category, sub_category: $sub_category})-[:BELONGS_TO]->(sc)
        MERGE (e1)-[:RELATED {relation: $relation, user_id: $user_id, review: $cleaned_review_content, rating: $rating}]->(e2)
        ''', entity1=entity1, entity2=entity2, type_=type_, relation=relation, sentiment=sentiment, brand=brand, category=category, sub_category=sub_category, user_id=user_id, cleaned_review_content=cleaned_review_content, rating=rating)

    def retrieve_graph_data(self):
        with self.driver.session() as session:
            result = session.run('''
            MATCH (e1:Entity)-[r:RELATED]->(e2:Entity)
            RETURN e1.name as Entity1, e2.name as Entity2, r.relation as Relation
            ''')
            return result.data()
if __name__ == "__main__":
    pass