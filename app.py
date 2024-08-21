from flask import Flask, render_template, request, redirect, url_for
from database import DatabaseManager
from gpt_processor import GPTProcessor
from text_preprocessing import TextPreprocessor
from neo4j_manager import Neo4jManager
import os
import pandas as pd

app = Flask(__name__)

# Configuration
DB_PATH = 'amazon_reviews.db'
NEO4J_URI = "neo4j+s://67d73379.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = ""
OPENAI_API_KEY = ''

# Initialize components
db_manager = DatabaseManager(DB_PATH)
gpt_processor = GPTProcessor(OPENAI_API_KEY)
text_preprocessor = TextPreprocessor()
neo4j_manager = Neo4jManager(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get input from form
        review_text = request.form['review_text']
        user_id = request.form['user_id']
        review_rating = request.form['review_rating']
        brand = request.form['brand']
        category = request.form['category']
        sub_category = request.form['sub_category']

        # Preprocess text
        cleaned_text = text_preprocessor.preprocess(review_text)

        # Process with GPT and store in DB
        entities_dict = gpt_processor.extract_entities(cleaned_text)
        print("Entities Dictionary:- \n",entities_dict)
        entities_df = gpt_processor.prepare_dataframe(entities_dict, user_id, review_rating, brand, category, sub_category)
        db_manager.insert_data(cleaned_text, entities_df)

        # Load data to Neo4j
        neo4j_manager.load_data_from_sqlite(db_path=DB_PATH)

        return redirect(url_for('show_graph'))

    return render_template('index.html')

@app.route('/graph')
def show_graph():
    # Retrieve graph data from Neo4j
    graph_data = neo4j_manager.retrieve_graph_data()
    return render_template('graph.html', graph_data=graph_data)

if __name__ == "__main__":
    app.run(debug=True)
