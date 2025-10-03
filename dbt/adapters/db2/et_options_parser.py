import os
import yaml
from typing import Dict

class ETOptions:
    def __init__(self, options: Dict):
        self.options = options


def et_options_constructor(loader, node):
    """
    Returns a dict of values written in et_options.yaml file
    in the client/fe project.
    """
    values = loader.construct_mapping(node)
    et_options_obj: ETOptions = ETOptions(values)
    return et_options_obj


def etoptions_representer(dumper, data: ETOptions):
    return dumper.represent_mapping('!ETOptions', {k: v for k, v in data.options.items()})


def parse_et_options_yaml(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def get_et_options_as_string(user_file_path: str):
    yaml.SafeLoader.add_constructor('!ETOptions', et_options_constructor)
    et_options_data = parse_et_options_yaml(user_file_path)
    if not et_options_data:
        return ""
    to_be_returned = ""
    for k, v in et_options_data[0].options.items():
        to_be_returned += f"{k} {v}\n"
    return to_be_returned

def create_et_options(project_path):
    yaml.add_representer(ETOptions, etoptions_representer)
    et_options = ETOptions(options={'SkipRows': '1', 'Delimiter': "','", 'DateDelim': "'-'", 'MaxErrors': '0'})
    with open(f"{project_path}/et_options.yml", "w") as file:
        yaml.dump([et_options], file, default_flow_style=False)
