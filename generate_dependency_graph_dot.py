import sys
import pygraphviz as pgv
from modelrecords.repository import Repository

styles = {
    'family': dict(shape="house", style="rounded, filled", penwidth=0.5, height=0.25, fillcolor="#CBC3E3", fontname="Helvetica"),
    'dataset': dict(shape="cylinder", style="rounded, filled", penwidth=0.5, width=0.75, height=0.25, fillcolor="#E0B7F3", fontname="Helvetica"),
    'model': dict(shape="box", style="rounded, filled", penwidth=0.5, height=0.25, fontcolor="#FFF", fillcolor="#800080", fontname="Helvetica")
}


def render_modelgraph(nodes, edges, records):
    G = pgv.AGraph(directed=True, rankdir="L", strict=False, nodesep=0.2, style='rounded', overlap=True, splines='ortho')
    for node in nodes:
        node_style = styles[records[node].type]
        G.add_node(node, **node_style, label=records[node].model_name)
    for A, B in edges:
        G.add_edge(B, A, color="#545454", penwidth=0.75, shape='rect', arrowsize=0.75)

    G.node_attr.update(fontsize="9", fontcolor="black", color="black")
    G.layout(prog="dot") 
    return G

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_dependency_graph_dot.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]
    repo = Repository()
    mr = repo.find(model_name)
    G = render_modelgraph(*repo.find_parent_packages(mr))
    G.draw(f'{model_name}.svg', prog='dot')

    html_template = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Dependency Graph</title>
</head>
<body>
    <div id='graph'>
        <img src='{model_name}.svg' alt='Dependency Graph'>
    </div>
</body>
</html>
"""

    with open(f'{model_name}.html', 'w') as f:
        f.write(html_template)
