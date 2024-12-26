import numpy as np
import networkx as nx
import pandas as pd
import ast

def describe_graph(G, weights=True, shortest_paths = True):    
    print("Number of nodes: ", G.number_of_nodes())
    print("Number of edges: ", G.number_of_edges())
    if weights:
        print("Average edge weight: ", np.mean([data['weight'] for _, _, data in G.edges(data=True)]))
        print("Smallest edge weight: ", min([data['weight'] for _, _, data in G.edges(data=True)]))
        print("Largest edge weight: ", max([data['weight'] for _, _, data in G.edges(data=True)]))

    components = list(nx.connected_components(G))
    lcc = max(components, key=len)
    print("Number of connected components: ", nx.number_connected_components(G), 
          "\n\tamong which the number of components with more than one node:" , 
          len([c for c in components if len(c) > 1]))
    print("Size of largest connected component:", len(lcc))

    if shortest_paths:
        lcc_all_shortest_path_lengths = nx.all_pairs_shortest_path_length(G.subgraph(lcc))
        lcc_all_shortest_path_lengths = [length for src, tgts in lcc_all_shortest_path_lengths for tgt, length in tgts.items() if length > 0]
        print(f"Average shortest path length: {sum(lcc_all_shortest_path_lengths)/len(lcc_all_shortest_path_lengths):.2f}")
        print("Diameter: ", nx.diameter(G))


def get_column_counts(artists_df, column):
    return (artists_df[column]).value_counts()

def get_column_counts_adjusted(artists_df, column):
    return (artists_df[column]).value_counts(normalize=True)

def get_column_average(artists_df, column):
    return (artists_df[column]).mean()

def get_column_std(artists_df, column):
    return (artists_df[column]).std()

def get_locations_average(artists_df):
    all_people_locations = []
    for index, row in artists_df.iterrows():
        locations = ast.literal_eval(row['locations'])
        all_people_locations.extend(locations)

    return pd.Series(all_people_locations).value_counts(normalize=True)

def get_female_percentage(artists_df):
    values = (artists_df['gender'].value_counts(normalize=True))
    try:
        values_known = values['male'] + values['female']
    except KeyError:
        try:
            values_known = values['male']
            if values_known == 0:
                return None
            else :
                return 0
        except KeyError:
            try:
                values_known = values['female']
                if values_known == 0:
                    return None
                else:
                    return 100
            except KeyError:
                return None
    return 100*values['female'] / values_known


def clustering_coefficient(G):
    """Calculated for each node, returns a list of coefficients"""
    return list(nx.clustering(G).values())

def threshold_filter(G, threshold):
    edges_to_remove = [(u, v) for u, v, data in G.edges(data=True) if data['weight'] < threshold]
    G.remove_edges_from(edges_to_remove)
    G.remove_nodes_from(list(nx.isolates(G)))
    return G

def compute_disparity_filter_probas(G):
    edge_probas = {}
    for node in G.nodes():
        node_edges = G.edges(node, data='weight')
        k = len(node_edges)
        strength = sum([w for _, _, w in node_edges])

        for u, v, w in node_edges:
            p_ij = (1 - w / strength) ** (k - 1)
            edge_probas[(u, v)] = p_ij

    return edge_probas