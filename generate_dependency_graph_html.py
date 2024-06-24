import sys
import json
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
        print("Usage: python generate_dependency_graph_html.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]
    repo = Repository()
    mr = repo.find(model_name)
    graph_data = render_modelgraph(*repo.find_parent_packages(mr))
    with open(f'{model_name}.json', 'w') as f:
        json.dump(graph_data, f)

    html_template = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Dependency Graph</title>
    <script src='https://d3js.org/d3.v7.min.js'></script>
</head>
<body>
    <div id='graph'></div>
    <script>
        const graphData = {json.dumps(graph_data)};

        const width = 960;
        const height = 600;

        const svg = d3.select('#graph').append('svg')
            .attr('width', width)
            .attr('height', height);

        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2));

        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(graphData.links)
            .enter().append('line')
            .attr('stroke-width', function(d) { return d.style.penwidth; })
            .attr('stroke', function(d) { return d.style.color; });

        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(graphData.nodes)
            .enter().append('circle')
            .attr('r', 10)
            .attr('fill', function(d) { return d.style.fillcolor; })
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        node.append('title')
            .text(function(d) { return d.label; });

        simulation
            .nodes(graphData.nodes)
            .on('tick', ticked);

        simulation.force('link')
            .links(graphData.links);

        function ticked() {
            link
                .attr('x1', function(d) { return d.source.x; })
                .attr('y1', function(d) { return d.source.y; })
                .attr('x2', function(d) { return d.target.x; })
                .attr('y2', function(d) { return d.target.y; });

            node
                .attr('cx', function(d) { return d.x; })
                .attr('cy', function(d) { return d.y; });
        }

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    </script>
</body>
</html>
"""

    with open(f'{model_name}.html', 'w') as f:
        f.write(html_template)
