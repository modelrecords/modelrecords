import os
from modelrecords.repository import Repository
from pelican import signals

def load_repository_data(generator):
    repository = Repository()
    generator.context['repo'] = repository

    pkg_list = repository.all_packages()

    # Iterate through the dictionary items
    for key in pkg_list:
        item_name = 'Untitled'
        item_pkg_name = key

        content_dir = os.path.join('content/pages', item_pkg_name)
        os.makedirs(content_dir, exist_ok=True)

        content_file_model = os.path.join(content_dir, 'model.md')
        with open(content_file_model, 'w') as f:
            f.write(f"Title: {item_name}\n")
            f.write(f"URL: {item_pkg_name}/model\n")
            f.write(f"save_as: {item_pkg_name}/model.html\n")
            f.write(f"template: card_model\n")
            f.write(f"model_pkg_name: {item_pkg_name}\n\n")

        content_file_umr = os.path.join(content_dir, 'umr.md')
        with open(content_file_umr, 'w') as f:
            f.write(f"Title: {item_name}\n")
            f.write(f"URL: {item_pkg_name}/umr\n")
            f.write(f"save_as: {item_pkg_name}/umr.html\n")
            f.write(f"template: card_umr\n")
            f.write(f"original_url: {item_pkg_name}/index.html\n")
            f.write(f"model_pkg_name: {item_pkg_name}\n\n")

    # Add the data dict to the context
    generator.context['mr'] = {}

def register():
    signals.generator_init.connect(load_repository_data)
