import os
import yaml
from modelrecord.repository import Repository
from pelican import signals

def add_repository_yaml_data(generator):
    repository = Repository(base_repo_path='../repository')

    pkg_list = repository.all_packages()
    data_list = []

    for pkg in pkg_list:
        data_list.append(repository.load_modelrecord_yaml(pkg))

    for item in data_list:
        item_name = item.pc.metadata.name
        item_version = item.pc.metadata.version
        item_name_version = item_name.lower()+'_v'+str(item_version)
        content_dir = os.path.join('content/pages', item_name_version)
        os.makedirs(content_dir, exist_ok=True)
        content_file_model = os.path.join(content_dir, 'model.md')
        with open(content_file_model, 'w') as f:
            f.write(f"Title: {item_name}\n")
            f.write(f"URL: {item_name_version+'/model'}\n")
            f.write(f"save_as: {item_name_version+'/model.html'}\n")
            f.write(f"template: {'card_model'}\n")
            f.write(f"model_name: {item_name}\n")
            f.write(f"model_version: {item_version}\n\n")
        content_file_umr = os.path.join(content_dir, 'umr.md')
        with open(content_file_umr, 'w') as f:
            f.write(f"Title: {item_name}\n")
            f.write(f"URL: {item_name_version+'/umr'}\n")
            f.write(f"save_as: {item_name_version+'/umr.html'}\n")
            f.write(f"template: {'card_umr'}\n")
            f.write(f"model_name: {item_name}\n")
            f.write(f"model_version: {item_version}\n\n")

    # Add the data list to the context
    generator.context['repository_yaml_data'] = data_list
    # generator.context['repository'] = repository

def register():
    signals.generator_init.connect(add_repository_yaml_data)
