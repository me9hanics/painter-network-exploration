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

def describe_measures(artists_df, print_results=True):
    nationality = get_column_counts_adjusted(artists_df, 'Nationality')
    citizenship = get_column_counts_adjusted(artists_df, 'citizenship')
    gender = get_female_percentage(artists_df)
    birth_year = get_column_average(artists_df, 'birth_year')
    wikiart_pictures_count = get_column_average(artists_df, 'wikiart_pictures_count')
    styles = get_column_counts_adjusted(artists_df, 'styles')
    movement = get_column_counts_adjusted(artists_df, 'movement')

    def get_top_10_items(data):
        return [(k, round(v, 3)) for k, v in list(data.items())[:10]]

    top10s_df = pd.DataFrame({
        'Nationality': [item[0] for item in get_top_10_items(nationality)],
        'Nationality ratio': [item[1] for item in get_top_10_items(nationality)],
        'Citizenship': [item[0] for item in get_top_10_items(citizenship)],
        'Citizenship ratio': [item[1] for item in get_top_10_items(citizenship)],
        'Movement': [item[0] for item in get_top_10_items(movement)],
        'Movement ratio': [item[1] for item in get_top_10_items(movement)],
        'Styles': [item[0] for item in get_top_10_items(styles)],
        'Styles ratio': [item[1] for item in get_top_10_items(styles)],
    })
    top10s_df.index = np.arange(1, 11)

    summary_stats = {
        "fem_pct": round(gender, 3),
        "avg_birth_year": round(birth_year, 3),
        "avg_wikiart_pics_count": round(wikiart_pictures_count, 3)
    }

    if print_results:
        print("Percentage of females in the graph: ", summary_stats["fem_pct"])
        print("Average birth year in the graph: ", summary_stats["avg_birth_year"])
        print("Average number of pictures on WikiArt: ", summary_stats["avg_wikiart_pics_count"])
        return top10s_df
    return top10s_df, summary_stats

def get_column_counts(artists_df, column):
    return (artists_df[column]).value_counts()

def get_column_counts_adjusted(artists_df, column, round_to=3):
    if round_to:
        return (artists_df[column]).value_counts(normalize=True).round(round_to)
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

def neighbours_avg_degree(G, node):
    return np.mean([G.degree(neighbour) for neighbour in G.neighbors(node)])

def average_knn_for_k(k_nn_dict, k):
    return np.mean([data["k_nn"] for data in k_nn_dict.values() if data["degree"] == k])

def average_knn(k_nn_dict):
    k_values = np.unique([data["degree"] for data in k_nn_dict.values()])
    k_nn_values_per_k = {k : average_knn_for_k(k_nn_dict, k) for k in k_values}
    return k_nn_values_per_k

def rich_club_approximate(G):
    """Only relevant for high degree nodes, as k -> inf !!!"""
    rich_club = nx.rich_club_coefficient(G, normalized=False) # don't normalize, it is slow and can throw errors
    average_degree = np.mean([G.degree(node) for node in G.nodes()])
    factor = 1 / (G.number_of_nodes() * average_degree)
    rich_club_normalized = {k: v / (factor * k**2) for k, v in rich_club.items() if k > 0}
    return rich_club_normalized