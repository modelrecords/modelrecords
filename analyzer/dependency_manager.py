import yaml
from typing import List, Dict


class Dependency:
    def __init__(self, upstream_deps: List[str]):
        self.type = ""
        self.metadata = {"name": "", "refs": [], "description": ""}
        self.safety = {"nsfw": "", "csam": "", "violence": ""}
        self.relations = {"upstream": upstream_deps}


def build_yaml_structure(upstream_deps: List[str]) -> Dependency:
    return Dependency(upstream_deps)


def write_yaml(dependency: Dependency) -> None:
    data = yaml.dump(dependency.__dict__, default_flow_style=False)
    print(data)
    # with open("dependencies.yaml", "w") as file:
    #     file.write(data)
