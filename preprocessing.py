import re
import nltk
import sqlite3
import openai
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('punkt')


class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """
        Load CSV data into a pandas DataFrame.
        """
        df = pd.read_csv(self.file_path)
        return df


class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text):
        """
        Perform basic text cleaning: lowercasing, removing special characters and digits.
        """
        text = re.sub(r'\W', ' ', str(text))
        text = re.sub(r'\s+', ' ', text)
        text = text.lower()
        return text

    def tokenize_text(self, text):
        """
        Tokenize text and remove stopwords.
        """
        tokens = word_tokenize(text)
        filtered_words = [word for word in tokens if word not in self.stop_words]
        return ' '.join(filtered_words)

    def preprocess(self, text):
        """
        Apply all preprocessing steps.
        """
        cleaned_text = self.clean_text(text)
        tokenized_text = self.tokenize_text(cleaned_text)
        return tokenized_text



class EntityExtractor:
    def __init__(self, api_key):
        openai.api_key = api_key

    def extract_entities(self, text):
        """
        Extract entities using GPT-3.
        """
        system_message = "You are provided with Amazon product reviews from user. Use the text to extract the necessary information from the query effectively. "
        user_message = f"""Extract entities (Product, Feature, Sentiment) from the following and return them in the specified JSON format. The output should use single or double quotes:\n 
        Review- {text} 
        """
        custom_function_ent = [
            {
                "name": "get_relation",
                "description": "Function to return entities and their relations in the required format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entity1": {"type": "string"},
                                    "entity2": {"type": "string"},
                                    "type": {"type": "string"},
                                    "relation": {"type": "string"}
                                },
                                "required": ["entity1", "entity2", "type", "relation"]
                            }
                        }
                    },
                    "required": ["entities"]
                }
            }
        ]

        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message}
        ]
        # print(system_message)
        # print(user_message)
        lm_client = openai.OpenAI(api_key=openai.api_key)
        response = lm_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.1,
            functions=custom_function_ent,
            function_call='auto'
        )
        # print(response,response.choices[0].message.function_call.arguments)
        # content = response.choices[0].message.function_call.arguments
        # try:
        #     # Convert the string response to a dictionary
        #     entities_relations = eval(content)
        # except SyntaxError:
        #     entities_relations = {"error": "Unable to parse the response."}
        # return entities_relations
        # Check if the function_call is present
        function_call = response.choices[0].message.function_call
        if not function_call:
            raise ValueError("The function_call was not executed. Please check the model response.")

        content = function_call.arguments
        
        try:
            # Convert the string response to a dictionary
            entities_relations = eval(content.replace("'", "\""))
            
            # Check if no entities are recognized
            if not entities_relations.get('entities'):
                raise ValueError("No entities recognized in the provided text.")
        
        except SyntaxError:
            entities_relations = {"error": "Unable to parse the response."}
        
        return entities_relations

class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def drop_table(self):
        """
        Drop the existing table if it exists.
        """
        self.cursor.execute('''
        DROP TABLE IF EXISTS processed_reviews
        ''')
        self.conn.commit()

    def create_table(self):
        """
        Create a table to store processed data.
        """
        self.drop_table()  # Drop the existing table to avoid schema conflicts
        
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
        """
        Insert processed data into the database.
        """
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
        """
        Close the database connection.
        """
        self.conn.close()

class ProcessingPipeline:
    def __init__(self, file_path, db_path, api_key):
        self.loader = DataLoader(file_path)
        self.preprocessor = TextPreprocessor()
        self.extractor = EntityExtractor(api_key)
        self.db_manager = DatabaseManager(db_path)

    def classify_sentiment(self, rating):
        """
        Classify sentiment based on rating.
        """
        if rating >= 4:
            return 'Positive'
        elif rating == 3:
            return 'Neutral'
        else:
            return 'Negative'

    def process(self):
        """
        Execute the entire processing pipeline.
        """
        df = self.loader.load_data()
        self.db_manager.create_table()

        for index, row in df.iterrows():
            # Combine Review Title and Review Content for a more comprehensive input
            full_review_text = f"{row['Review Title']} {row['Review Content']}"
            # Preprocess the combined text
            cleaned_text = self.preprocessor.preprocess(full_review_text)
            
            # Extract entities using the cleaned combined text
            try:
                entities_dict = self.extractor.extract_entities(cleaned_text)
                entities_df = pd.DataFrame(entities_dict['entities'])
                
                # Add additional context like User ID, Rating, Brand, Category, etc.
                entities_df['user_id'] = row['User Id']
                entities_df['rating'] = row['Review Rating']
                entities_df['brand'] = row['Brand']
                entities_df['category'] = row['Category']
                entities_df['sub_category'] = row['Sub Category']

                # Classify sentiment based on rating
                entities_df['sentiment'] = entities_df['rating'].apply(self.classify_sentiment)

                # Classify predefined relations (e.g., based on entity types and content)
                entities_df['relation'] = entities_df.apply(self.classify_relation, axis=1)

                if entities_df.empty:
                    print(f"Warning: No entities found for the review: {cleaned_text}")
                    continue

                print(entities_df)
                self.db_manager.insert_data(cleaned_text, entities_df)

            except ValueError as e:
                print(f"Error processing review: {cleaned_text} - {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                
        self.db_manager.close_connection()

    def classify_relation(self, row):
        """
        Classify predefined relations based on the extracted entities and their content.
        """
        entity2_lower = row['entity2'].lower()

        # Product-Feature Relations
        if 'ingredient' in entity2_lower or 'charcoal' in entity2_lower or 'magnesium' in entity2_lower:
            return 'Has Ingredient'
        if 'irritation' in entity2_lower or 'rash' in entity2_lower or 'sensitivity' in entity2_lower:
            return 'Causes'
        if 'scent' in entity2_lower or 'fragrance' in entity2_lower or 'smell' in entity2_lower:
            return 'Has Scent'
        if 'absorb' in entity2_lower or 'protection' in entity2_lower or 'long-lasting' in entity2_lower:
            return 'Provides Benefit'
        if 'price' in entity2_lower or 'expensive' in entity2_lower or 'cost' in entity2_lower:
            return 'Worth'
        if 'application' in entity2_lower or 'apply' in entity2_lower:
            return 'Easy To Apply'

        # Product-Sentiment Relations
        if 'like' in entity2_lower or 'love' in entity2_lower or 'recommend' in entity2_lower:
            return 'Liked By'
        if 'dislike' in entity2_lower or 'hate' in entity2_lower or 'not recommend' in entity2_lower:
            return 'Disliked By'
        if 'recommend' in entity2_lower:
            return 'Recommended By'
        if 'not recommend' in entity2_lower or 'avoid' in entity2_lower:
            return 'Not Recommended By'

        # Product-Usage Relations
        if 'sensitive skin' in entity2_lower or 'dry skin' in entity2_lower or 'oily skin' in entity2_lower:
            return 'Suitable For'
        if 'daily use' in entity2_lower or 'travel' in entity2_lower:
            return 'Used For'

        # Product-Performance Relations
        if 'effective' in entity2_lower or 'works' in entity2_lower:
            return 'Effective For'
        if 'lasts' in entity2_lower or 'durable' in entity2_lower:
            return 'Long-Lasting'
        if 'quick results' in entity2_lower or 'immediate' in entity2_lower:
            return 'Quick Results'

        # Product-Comparison Relations
        if 'better than' in entity2_lower or 'superior to' in entity2_lower:
            return 'Better Than'
        if 'worse than' in entity2_lower or 'inferior to' in entity2_lower:
            return 'Worse Than'

        # Default if no specific relation is found
        return 'Related To'


if __name__ == "__main__":
    # Define paths and API key
    csv_file_path = './amazon_com-product_reviews__20200101_20200331_sample.csv'
    database_path = 'amazon_reviews.db'
    openai_api_key = 'API-KEY'

    # Initialize and run the pipeline
    pipeline = ProcessingPipeline(csv_file_path, database_path, openai_api_key)
    pipeline.process()
