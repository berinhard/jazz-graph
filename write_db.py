import json
from py2neo import authenticate, Graph as Py2NeoGraph
from py2neo import Node, Relationship, Subgraph
from unipath import Path

graph_kwargs = {
    'host': 'localhost',
    'http_port': 7475,
    'bolt_port': 7688,
}

graph = Py2NeoGraph(**graph_kwargs)

GRAPH_JSON_FILE = Path(__file__).parent.child('data', 'jazz_musicians_graph.json')

if __name__ == '__main__':

    nodes_by_id = {}
    relationships = []
    with open(GRAPH_JSON_FILE) as fd:
        graph_data = json.load(fd)

        print('Generating nodes')
        for node_id, node_data in graph_data['nodes'].items():
            data = node_data.copy()
            node_type = data.pop('type')
            data['id'] = node_id
            nodes_by_id[node_id] = Node(node_type, **data)

        print('Generating relationships')
        for source, target, rel_data in graph_data['edges']:
            data = rel_data.copy()
            rel_type = data.pop('type')
            source_node = nodes_by_id[source]
            target_node = nodes_by_id[target]
            rel = Relationship(source_node, rel_type, target_node, **data)
            relationships.append(rel)

    print('Generating graph')
    db_graph = Subgraph(nodes_by_id.values(), relationships)

    print('Writting nodes')
    for node in nodes_by_id.values():
        graph.create(node)
    print('Writting relationships')
    for rel in relationships:
        graph.create(rel)
