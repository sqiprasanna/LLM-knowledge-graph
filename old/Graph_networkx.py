import networkx as nx
import matplotlib.pyplot as plt
import sqlite3

class GraphVisualizer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.cursor = self.conn.cursor()

    def load_data(self):
        """
        Load data from the SQLite database.
        """
        self.cursor.execute('''
        SELECT user_id, entity1, entity2, relation, sentiment, brand, category, sub_category
        FROM processed_reviews
        ''')
        return self.cursor.fetchall()

    def create_graph(self, data):
        """
        Create a graph using NetworkX.
        """
        G = nx.DiGraph()  # Create a directed graph

        for row in data:
            user_id, entity1, entity2, relation, sentiment, brand, category, sub_category = row
            G.add_node(entity1, sentiment=sentiment, brand=brand, category=category, sub_category=sub_category)
            G.add_node(entity2, sentiment=sentiment, brand=brand, category=category, sub_category=sub_category)
            G.add_edge(entity1, entity2, relation=relation, user_id=user_id)
        
        return G

    def visualize_graph(self, G):
        """
        Visualize the graph using matplotlib.
        """
        pos = nx.spring_layout(G)  # Layout for the nodes
        
        # Draw the nodes with labels
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_color='gray', font_size=10, font_weight='bold', arrows=True)

        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'relation')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        plt.show()

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()

if __name__ == "__main__":
    # Path to the SQLite database
    database_path = 'amazon_reviews.db'

    # Initialize the GraphVisualizer
    graph_visualizer = GraphVisualizer(database_path)

    # Load data from the SQLite database
    data = graph_visualizer.load_data()

    # Create a graph using NetworkX
    G = graph_visualizer.create_graph(data)

    # Visualize the graph
    graph_visualizer.visualize_graph(G)

    # Close the database connection
    graph_visualizer.close_connection()
