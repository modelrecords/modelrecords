import os
from pelican import signals
from modelrecords.repository import Repository
from generate_dependency_graph_dot import render_modelgraph


def generate_svgs(pelican):
    output_path = os.path.join(pelican.settings['OUTPUT_PATH'], 'static', 'svg')
    os.makedirs(output_path, exist_ok=True)

    repo = Repository()
    content_path = pelican.settings['PATH']
    
    # Iterate over content files to identify models
    for root, dirs, files in os.walk(content_path):
        for file in files:
            if file.endswith('.md') or file.endswith('.rst'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    # Extract model name from content metadata
                    model_name = extract_model_name(content)
                    if model_name:
                        mr = repo.find(model_name)
                        nodes, edges, records = repo.find_parent_packages(mr)
                        G = render_modelgraph(nodes, edges, records)
                        svg_path = os.path.join(output_path, f'{model_name}.svg')
                        G.draw(svg_path, prog='dot')


def extract_model_name(content):
    # Logic to extract model name from content metadata
    for line in content.split('\n'):
        if line.startswith('model_pkg_name:'):
            return line.split(':')[1].strip()
    return None


def register():
    signals.finalized.connect(generate_svgs)
