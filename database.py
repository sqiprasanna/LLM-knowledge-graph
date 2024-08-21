import sqlite3
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cleaned_review_content TEXT,
            user_id TEXT,
            entity1 TEXT,
            entity2 TEXT,
            type TEXT,
            relation TEXT,
            rating REAL,
            sentiment TEXT,
            brand TEXT,
            category TEXT,
            sub_category TEXT
        )
        ''')
        self.conn.commit()

    def insert_data(self, cleaned_review_content, entities_df):
        if entities_df.empty:
            print("Warning: No entities to insert into the database.")
            return
        
        for _, row in entities_df.iterrows():
            self.cursor.execute('''
            INSERT INTO processed_reviews (
                cleaned_review_content, user_id, entity1, entity2, type, relation, 
                rating, sentiment, brand, category, sub_category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cleaned_review_content,
                row['user_id'],
                row['entity1'],
                row['entity2'],
                row['type'],
                row['relation'],
                row['rating'],
                row['sentiment'],
                row['brand'],
                row['category'],
                row['sub_category']
            ))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
