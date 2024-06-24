import sys
sys.path.insert(0, '/Users/davidgilmore/Workspace/modelrecords2')

import graphviz
from modelrecords.repository import Repository

styles = {
    'model': {'shape': 'box', 'style': 'filled', 'fillcolor': 'lightblue'},
    'dataset': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgreen'},
    'metric': {'shape': 'diamond', 'style': 'filled', 'fillcolor': 'lightyellow'},
    'default': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgrey'}
}


def render_modelgraph(nodes, edges, records):
    G = graphviz.Digraph(format='png')
    G.attr(rankdir="L", strict="false", nodesep="0.2", style='rounded', overlap="true", splines='ortho')
    for node in nodes:
        node_style = styles.get(records[node].type, styles['default'])
        if hasattr(records[node], 'safety') and records[node].safety.csam:
            node_style['fillcolor'] = 'red'
        G.node(node, **node_style, label=records[node].model_name)
    for A, B in edges:
        G.edge(B, A, color="#545454", penwidth="0.75", shape='rect', arrowsize="0.75")

    G.node_attr.update(fontsize="9", fontcolor="black", color="black")
    return G

repo = Repository()
mr = repo.find('vicuna-13b')
graph = render_modelgraph(*repo.find_parent_packages(mr))
graph.render(filename='vicuna-13b', engine='dot')

mr = repo.find('plip')
graph = render_modelgraph(*repo.find_parent_packages(mr))
graph.render(filename='plip', engine='dot')

mr = repo.find('LLaVA-1.6-Vicuna-13B')
graph = render_modelgraph(*repo.find_parent_packages(mr))
graph.render(filename='LLaVA-1.6-Vicuna-13B', engine='dot')
