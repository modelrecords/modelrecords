import os
import yaml
from pelican import signals

def add_repository_yaml_data(generator):
    # Assuming 'file_list' is your list of YAML files
    file_list = [
      'bloomz/bloomz-1.0.0.yaml',
      'claude2/claude2-1.0.0.yaml',
    ]
    data_list = []

    for file_name in file_list:
        with open('../../../repository/' + file_name, 'r') as stream:
            try:
                # Load the YAML file
                data = yaml.safe_load(stream)
                data_list.append(data)
            except yaml.YAMLError as exc:
                print(exc)

    # Add the data list to the context
    generator.context['repository_yaml_data'] = data_list

def register():
    signals.generator_init.connect(add_repository_yaml_data)
