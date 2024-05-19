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

    # Add the data list to the context
    generator.context['repository_yaml_data'] = data_list

def register():
    signals.generator_init.connect(add_repository_yaml_data)
