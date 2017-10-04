from unipath import Path
import json
import networkx as nx

GRAPH_JSON_FILE = Path(__file__).parent.child('data', 'jazz_musicians_graph.json')


def flatten_edges(master_graph):
    for source, targets in graph.adjacency():
        for target, rels in targets.items():
            for rel_data in rels.values():
                yield (source, target, rel_data)


def extract_recorded_graph(master_graph):
    graph = nx.Graph()
    graph.add_nodes_from(master_graph.nodes())

    flatten = flatten_edges(master_graph)
    graph.add_edges_from([(s, t) for s, t, r in flatten if r['type'] == 'RECORDED'])

    return graph


def extract_played_with_graph(master_graph):
    graph = nx.Graph()
    graph.add_nodes_from(master_graph.nodes())

    flatten = flatten_edges(master_graph)
    for source, target, data in flatten:
        if not data['type'] == 'PLAYED_WITH':
            continue
        if not graph.has_edge(source, target):
            graph.add_edge(source, target, weight=1, **data)
        graph.edges[(source, target)]['weight'] += 1

    isolates = nx.isolates(graph)
    graph.remove_nodes_from([n for n in isolates])

    return graph


def top_10_albuns(recorded_graph, master_graph):
    centralities = nx.eigenvector_centrality(recorded_graph)
    is_musician = lambda n: master_graph.node[n]['type'] == 'RELEASE'
    sorted_nodes = [n for n in sorted(centralities, key=centralities.get, reverse=True) if is_musician(n)]
    return sorted_nodes[:10], centralities


def top_10_recorders(recorded_graph, master_graph):
    centralities = nx.degree_centrality(recorded_graph)
    is_musician = lambda n: master_graph.node[n]['type'] == 'MUSICIAN'
    sorted_nodes = [n for n in sorted(centralities, key=centralities.get, reverse=True) if is_musician(n)]
    return sorted_nodes[:10], centralities


def top_10_side(recorded_graph, master_graph):
    centralities = nx.eigenvector_centrality(recorded_graph, weight='weight')
    is_musician = lambda n: master_graph.node[n]['type'] == 'MUSICIAN'
    sorted_nodes = [n for n in sorted(centralities, key=centralities.get, reverse=True) if is_musician(n)]
    return sorted_nodes[:10], centralities


if __name__ == '__main__':
    graph = nx.MultiDiGraph()

    with open(GRAPH_JSON_FILE) as fd:
        graph_data = json.load(fd)
        graph.add_nodes_from(graph_data['nodes'].items())
        graph.add_edges_from(graph_data['edges'])

    recorded_graph = extract_recorded_graph(graph)

    print("Top 10 Recorders")
    top_10, degrees = top_10_recorders(recorded_graph, graph)
    for i, node in enumerate(top_10[:10]):
        data = graph.node[node]
        instruments = '/'.join(data['roles'])
        print("{}) {} / score: {}".format(i + 1, '{} - {}'.format(data['name'], instruments), degrees[node]))

    print()
    print("Top 10 Albuns")
    top_10, eigenvector = top_10_albuns(recorded_graph, graph)
    for i, node in enumerate(top_10[:10]):
        data = graph.node[node]
        print("{}) {} / score: {}".format(i + 1, '{} - {}'.format(data['title'], data['year']), eigenvector[node]))

    played_with_graph = extract_played_with_graph(graph)
    top_10, side = top_10_side(played_with_graph, graph)
    print()
    print("Top 10 Sidemen")
    for i, node in enumerate(top_10[:10]):
        data = graph.node[node]
        instruments = '/'.join(data['roles'])
        print("{}) {} / score: {}".format(i + 1, '{} - {}'.format(data['name'], instruments), side[node]))
