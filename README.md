# LLM-Driven Knowledge Graph for Customer Review Analysis and Product Recommendation
## DE & Ingestion
ETL using Airflow (get reviews from online reddit/some website real time)
Amazon product review -> data contract -> store in S3/sqlite/AWS-RDS/GCP-BigQuery
Store in relation or graph database

## LLM Fine tuning
Fine tune LLM (BERT, GPT-3) on customer review data -> Entity, relation and sentiment extraction. 
1. Extract entities & Extract relations b/w entities (GPT-3.5)
2. sentiment of sentence (fine tune BERT/LLM model to get sentiment)
3. store entities (products, customers, features) and their relation in a relational database/CSV
4. knowledge graph that captures relation b.w customers, products, features and sentiments.

## Knowledge graph
1. Entities (Nodes)
    * Customer: Represents the individuals who are providing reviews or feedback.
    * Product: Represents the items that customers are reviewing.
    * Feature: Represents specific aspects or attributes of a product (e.g., battery life, camera quality).
    * Sentiment: Represents the emotional tone or sentiment associated with a customer's review of a feature (e.g., positive, negative, neutral).

2. Relationships (Edges)
    * REVIEWED: Connects a Customer to a Product, indicating that the customer has reviewed the product.
    * HAS_FEATURE: Connects a Product to a Feature, indicating that the product has a particular feature.
    * ASSOCIATED_WITH: Connects a Feature to a Sentiment, indicating the sentiment associated with a particular feature based on customer feedback.

## UI & Neo4J

## Docker

## Deploy to EC2

## Monitoring and Logging

## Unit Testing


## Flask
1. Upload a file with specific data contract or create one and store it in DB
   * In the background compute all things like extract entities, relations and sentiment. (With custom function - outputs in JSON format)
   * Read the JSON format and provide it to Neo4J for visualization


