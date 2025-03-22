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

### Graph measures

def random_config_communities(comm, seed=1):
    #nested list of communities: e.g. [[1,2,3], [4,5,6]]
    #returns a list of communities with exact same distribution, but nodes randomly shuffled across communities
    comm_lengths = [len(c) for c in comm]
    flattened = [node for c in comm for node in c]
    np.random.seed(seed)
    np.random.shuffle(flattened)
    section_indices = list(np.cumsum(comm_lengths))
    return [flattened[i:j] for i, j in zip([0] + section_indices, section_indices)]

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

def coreness(G, partition):
    edges = list(G.edges())
    cores = partition[0]
    #peripheries = partition[1]
    ro = 0
    for i,j in edges:
        if (i in cores) and (j in cores):
            ro += 1
    return ro

def coreness_corrected(G, partition):
    partition_randomized = random_config_communities(partition)
    ro = coreness(G, partition)
    ro_config = coreness(G, partition_randomized)
    return ro/ro_config

def extract_rich_core(G, weight='weight', weight_default = 1):
    """Returns the core/periphery structure of a weighted undirected network (see [1]).
       Code taken from Iacopo Iacopini [2], but updated the method (replacing outdated functions).
        
        Args
        ----
        G: NetworkX weighted undirected graph.
        
        weight: string (default='weight')
        Key for edge data used as the edge weight w_ij.
        
        Returns
        -------
        sigmas: list
        List of σ_i values associated to each node i of the network, representing the strength of the node i
        after rescaling the weights in units of the minimal weight. σ_i = ∑j⌈w_ij/w_min⌉
        
        ranked_nodes: list
        List of nodes ranked by normalised strength σ_i.
        
        r_star: int
        r_star (r∗) is the index of the core boundary node, such that σ^{+}_r∗>σ^{+}_r for r > r*, where
        σ^{+}_i is the portion of σ_i that connects node i, ranked r, to nodes of a higher rank.
        
        
        References
        ----------
        .. [1] Ma A and Mondragón RJ (2015).
        "Rich-cores in networks".
        PLoS One 10(3):e0119678.
        
        .. [2] https://github.com/iaciac/py-network-rich-core/

        """
    
    if G.is_multigraph():
        raise nx.NetworkXNotImplemented("Function only implemented for simple graphs.")
    
    #TODO If no weight, use degree, and in-degree for

    G = G.copy()
    
    #Use weight = weight_default for nodes without a weight
    weights = [d.get(weight, weight_default) for _, _, d in G.edges(data=True)]
    minw = min(weights)

    for u, v, data in G.edges(data=True):
        data[weight] = data.get(weight, 1) / minw
    
    strength = dict(G.degree(weight="weight"))
    ranked_nodes = sorted(strength, key=strength.get, reverse=True)
    
    sigmas = []
    for i in ranked_nodes:
        sigma_i = sum(strength[j] for j in G.neighbors(i) if strength[j] > strength[i])
        sigmas.append(sigma_i)
    
    #Find r_star, the core boundary index
    r_star = sigmas.index(max(sigmas))
    
    return sigmas, ranked_nodes, r_star

### Partition comparisons

def community_LUT(comm_nested_list):
    lut = {}
    for i, comm in enumerate(comm_nested_list):
        for node in comm:
            lut[node] = i
    return lut

def index_matrix_values(comm1, comm2):
    #Assuming comm1 and comm2 include the same nodes
    a00 = 0; a11 = 0; a01 = 0; a10 = 0 #PEP8 would not approve
    comm1_lut = community_LUT(comm1)
    comm2_lut = community_LUT(comm2)
    if set(comm1_lut.keys()) != set(comm2_lut.keys()):
        raise ValueError("Communities must have the same nodes")
    nodes = list(comm1_lut.keys())
    pairs = [(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i+1, len(nodes))]
    for i, j in pairs:
        if comm1_lut[i] == comm1_lut[j]:
            if comm2_lut[i] == comm2_lut[j]:
                a11 += 1
            else:
                a10 += 1
        else:
            if comm2_lut[i] == comm2_lut[j]:
                a01 += 1
            else:
                a00 += 1
    return a00, a01, a10, a11

def rand_index(comm1, comm2):
    a00, a01, a10, a11 = index_matrix_values(comm1, comm2)
    return (a00 + a11) / (a00 + a01 + a10 + a11)

def jaccard_index(comm1, comm2):
    a00, a01, a10, a11 = index_matrix_values(comm1, comm2)
    return a11 / (a01 + a10 + a11)
