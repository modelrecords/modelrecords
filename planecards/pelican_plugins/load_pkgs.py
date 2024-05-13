import os
import yaml
from planecards.repository import Repository
from pelican import signals

def add_repository_yaml_data(generator):
    repository = Repository(base_repo_path='../repository')

    pkg_list = repository.all_packages()
    data_list = []

    for pkg in pkg_list:
        data_list.append(repository.load_plane_card_yaml(pkg))
        # with open('../../../repository/' + file_name, 'r') as stream:
        #     try:
        #         # Load the YAML file
        #         data = yaml.safe_load(stream)
        #         data_list.append(data)
        #     except yaml.YAMLError as exc:
        #         print(exc)

    # Add the data list to the context
    generator.context['repository_yaml_data'] = data_list

def register():
    signals.generator_init.connect(add_repository_yaml_data)
