from unipath import Path
import json
import networkx as nx

from termcolor import cprint

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
    for source, target, rel_data in flatten:
        if rel_data['type'] != 'RECORDED':
           continue
        graph.add_edge(source, target, **rel_data)

    return graph


def extract_played_with_graph(master_graph):
    graph = nx.Graph()
    for n, data in master_graph.nodes(data=True):
        if data['type'] == 'MUSICIAN':
            graph.add_node(n, **data)

    flatten = flatten_edges(master_graph)
    for source, target, data in flatten:
        if not data['type'] == 'PLAYED_WITH':
            continue
        if not graph.has_edge(source, target):
            graph.add_edge(source, target, weight=1, **data)
        graph.edges[(source, target)]['weight'] += 1

    return graph

def top_10_recorders(recorded_graph, master_graph):
    centralities = nx.degree_centrality(recorded_graph)
    is_musician = lambda n: master_graph.node[n]['type'] == 'MUSICIAN'
    sorted_centralities = sorted(centralities, key=centralities.get, reverse=True)
    sorted_nodes = [n for n in sorted_centralities if is_musician(n)]
    return sorted_nodes[:10], centralities

def top_10_prolifc_musicians(played_with_graph, master_graph):
    centralities = nx.eigenvector_centrality(played_with_graph, weight='weight')
    sorted_centralities = sorted(centralities, key=centralities.get, reverse=True)
    return sorted_centralities[:10], centralities

def top_10_albuns(recorded_graph, master_graph):
    centralities = nx.eigenvector_centrality(recorded_graph)
    is_album = lambda n: master_graph.node[n]['type'] == 'RELEASE'
    sorted_centralities = sorted(centralities, key=centralities.get, reverse=True)
    sorted_nodes = [n for n in sorted_centralities if is_album(n)]
    return sorted_nodes[:10], centralities


if __name__ == '__main__':
    import networkx as nx

    graph = nx.MultiDiGraph()
    with open(GRAPH_JSON_FILE) as fd:
        graph_data = json.load(fd)
        graph.add_nodes_from(graph_data['nodes'].items())
        graph.add_edges_from(graph_data['edges'])

    recorded_graph = extract_recorded_graph(graph)
    played_with_graph = extract_played_with_graph(graph)
    cprint('##### About the Graphs', 'yellow')
    cprint('RECORDED Graph', 'red')
    cprint("\t {} nodes".format(recorded_graph.number_of_nodes()))
    cprint('\t {} edges'.format(recorded_graph.number_of_edges()))
    cprint('PLAYED_WITH Graph', 'red')
    cprint('\t {} nodes'.format(played_with_graph.number_of_nodes()))
    cprint('\t {} edges'.format(played_with_graph.number_of_edges()))

    print()
    cprint("##### Top 10 Recorders", 'yellow')
    top_10, degrees = top_10_recorders(recorded_graph, graph)
    for i, node in enumerate(top_10[:10]):
        data = graph.node[node]
        instruments = '/'.join(data['roles'])
        cprint("{}) {} / score: {}".format(i + 1, '{} - {}'.format(data['name'], instruments), degrees[node]), 'white')

    print()
    cprint("##### Top 10 Albuns", 'yellow')
    top_10, eigenvector = top_10_albuns(recorded_graph, graph)
    for i, node in enumerate(top_10[:10]):
        data = graph.node[node]
        cprint("{}) {} / score: {}".format(i + 1, '{} - {}'.format(data['title'], data['year']), eigenvector[node]), 'white')

    top_10, side = top_10_prolifc_musicians(played_with_graph, graph)
    print()
    cprint("##### Top 10 Prolific Musicians", 'yellow')
    for i, node in enumerate(top_10[:10]):
        data = graph.node[node]
        instruments = '/'.join(data['roles'])
        cprint("{}) {} / score: {}".format(i + 1, '{} - {}'.format(data['name'], instruments), side[node]), 'white')
