import networkx as nx
import matplotlib.pyplot as plt
import sqlite3

class GraphVisualizer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_graph_from_db(self):
        self.cursor.execute('''
        SELECT entity1, entity2, relation, sentiment
        FROM processed_reviews
        ''')
        rows = self.cursor.fetchall()

        G = nx.DiGraph()

        for row in rows:
            entity1, entity2, relation, sentiment = row
            G.add_node(entity1, sentiment=sentiment)
            G.add_node(entity2, sentiment=sentiment)
            G.add_edge(entity1, entity2, relation=relation)

        return G

    def visualize_graph(self, G):
        pos = nx.spring_layout(G)
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10, font_weight='bold', arrows=True)
        edge_labels = nx.get_edge_attributes(G, 'relation')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        plt.savefig('./static/graph.png')
        plt.close()

    def close_connection(self):
        self.conn.close()

if __name__ == "__main__":
    pass