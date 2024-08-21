import openai
import pandas as pd

class GPTProcessor:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.lm_client = openai.OpenAI(api_key=openai.api_key)


    def extract_entities(self, text):
        system_message = "You are provided with Amazon product reviews from user. Use the text to extract the necessary information from the query effectively."
        user_message = f"Extract entities (Product, Feature, Sentiment) from the following and return them in the specified JSON format: {text}"

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
        response = self.lm_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1500,
            temperature=0.1,
            functions=custom_function_ent,
            function_call='auto'
        )

        function_call = response.choices[0].message.function_call
        if not function_call:
            raise ValueError("The function_call was not executed. Please check the model response.")

        content = function_call.arguments
        print(content)
        try:
            entities_relations = eval(content.replace("'", "\""))
            if not entities_relations.get('entities'):
                raise ValueError("No entities recognized in the provided text.")
        except SyntaxError:
            entities_relations = {"error": "Unable to parse the response."}
        
        return entities_relations

    def prepare_dataframe(self, entities_dict, user_id, rating, brand, category, sub_category):
        entities_df = pd.DataFrame(entities_dict['entities'])
        entities_df['user_id'] = user_id
        entities_df['rating'] = rating
        entities_df['brand'] = brand
        entities_df['category'] = category
        entities_df['sub_category'] = sub_category
        entities_df['rating'] = entities_df['rating'].astype(int)
        entities_df['sentiment'] = entities_df['rating'].apply(self.classify_sentiment)
        entities_df['relation'] = entities_df.apply(self.classify_relation, axis=1)
        return entities_df

    def classify_sentiment(self, rating):
        if type(rating) != int: 
            return "No Rating"
        if rating >= 4:
            return 'Positive'
        elif rating == 3:
            return 'Neutral'
        else:
            return 'Negative'

    def classify_relation(self, row):
        entity2_lower = row['entity2'].lower()

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

        if 'like' in entity2_lower or 'love' in entity2_lower or 'recommend' in entity2_lower:
            return 'Liked By'
        if 'dislike' in entity2_lower or 'hate' in entity2_lower or 'not recommend' in entity2_lower:
            return 'Disliked By'
        if 'recommend' in entity2_lower:
            return 'Recommended By'
        if 'not recommend' in entity2_lower or 'avoid' in entity2_lower:
            return 'Not Recommended By'

        if 'sensitive skin' in entity2_lower or 'dry skin' in entity2_lower or 'oily skin' in entity2_lower:
            return 'Suitable For'
        if 'daily use' in entity2_lower or 'travel' in entity2_lower:
            return 'Used For'

        if 'effective' in entity2_lower or 'works' in entity2_lower:
            return 'Effective For'
        if 'lasts' in entity2_lower or 'durable' in entity2_lower:
            return 'Long-Lasting'
        if 'quick results' in entity2_lower or 'immediate' in entity2_lower:
            return 'Quick Results'

        if 'better than' in entity2_lower or 'superior to' in entity2_lower:
            return 'Better Than'
        if 'worse than' in entity2_lower or 'inferior to' in entity2_lower:
            return 'Worse Than'

        return 'Related To'

if __name__ == "__main__":
    pass