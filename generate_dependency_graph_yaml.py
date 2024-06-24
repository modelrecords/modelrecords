import sys
import yaml
from modelrecords.repository import Repository

styles = {
    'model': {'shape': 'box', 'style': 'filled', 'fillcolor': 'lightblue'},
    'dataset': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgreen'},
    'metric': {'shape': 'diamond', 'style': 'filled', 'fillcolor': 'lightyellow'},
    'default': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgrey'}
}


def render_modelgraph(nodes, edges, records):
    graph_data = {'nodes': [], 'links': []}
    for node in nodes:
        node_style = styles.get(records[node].type, styles['default'])
        graph_data['nodes'].append({'id': node, 'label': records[node].model_name, 'style': node_style})
    for A, B in edges:
        graph_data['links'].append({'source': B, 'target': A, 'style': {'color': '#545454', 'penwidth': 0.75, 'shape': 'rect', 'arrowsize': 0.75}})
    return graph_data

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_dependency_graph_yaml.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]
    repo = Repository()
    mr = repo.find(model_name)
    graph_data = render_modelgraph(*repo.find_parent_packages(mr))
    with open(f'{model_name}.yaml', 'w') as f:
        yaml.dump(graph_data, f)
