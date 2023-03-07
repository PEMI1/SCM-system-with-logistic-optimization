import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

segments = gpd.read_file('C:\\Users\\hp\\Desktop\\segment-intersection.shp')

G = nx.Graph()

for index, row in segments.iterrows():
    # Add nodes for each endpoint of the line segment
    node1 = (row['lat_n1'], row['long_n1'])
    node2 = (row['lat_n2'], row['long_n2'])
    G.add_node(node1)
    G.add_node(node2)

    # Add an edge between the two nodes
    G.add_edge(node1, node2, weight=row['length_m'])

# Draw the graph and label the nodes and edges
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

# Show the plot
plt.show()


def floyd_warshall_predecessor_and_distance(G, weight="weight"):
    from collections import defaultdict

    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    dist = defaultdict(lambda: defaultdict(lambda: float("inf")))
    for u in G:
        dist[u][u] = 0
    pred = defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not G.is_directed()
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = u
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = v
    for w in G:
        dist_w = dist[w]  # save recomputation
        for u in G:
            dist_u = dist[u]  # save recomputation
            for v in G:
                d = dist_u[w] + dist_w[v]
                if dist_u[v] > d:
                    dist_u[v] = d
                    pred[u][v] = pred[w][v]
    return dict(pred), dict(dist)

def reconstruct_path(source, target, predecessors):
    if source == target:
        return []
    prev = predecessors[source]
    curr = prev[target]
    path = [target, curr]
    while curr != source:
        curr = prev[curr]
        path.append(curr)
    return list(reversed(path))

def floyd_warshall(G, weight="weight"):
    # could make this its own function to reduce memory costs
    return floyd_warshall_predecessor_and_distance(G, weight=weight)[1]

result = floyd_warshall(G, "weight")
print(result)