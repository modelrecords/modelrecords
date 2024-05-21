from omegaconf import OmegaConf
import os
from pathlib import Path
from importlib import resources
from modelrecords.modelrecord import ModelRecord 
from modelrecords.utils import content_extract_text
from modelrecords.package_parser import PackageParser

BASE_REPO_PATH = f'{resources.files('modelrecords')}/repository'
RESERVED_FOLDERS = ['_refs']

class Repository:
    def __init__(self, base_repo_path=BASE_REPO_PATH):
        self.base_repo_path = os.path.normpath(base_repo_path)
        self.pkg_parser = PackageParser(self.base_repo_path)

    def modelrecord_folder(self, pkg:str):
        return f'{self.base_repo_path}/{pkg}'

    def find_in_repo(self, pkg_query:str):
        parsed = self.pkg_parser.parse_pkg_version_query(pkg_query)
        pkg = parsed['pkg']
        version = parsed['version']
        operand = parsed['operand']
        for candidate in sorted(os.listdir(self.modelrecord_folder(pkg)))[::-1]:
            can_parsed = self.pkg_parser.parse_pkg_version_query(candidate.replace('.yaml',''))
            if operand(version , can_parsed['version']):
                return f'{self.modelrecord_folder(pkg)}/{candidate}'
        raise f"No card found: {pkg_query}"
       
    def all_packages(self):
        pkgs = [d for d in os.listdir(self.base_repo_path) if d not in RESERVED_FOLDERS]
        return pkgs

    def find_parent_packages(self, model_record:ModelRecord):
        edges = []
        def find_parents(mr, indent=' '):
            for rel in mr.upstream_relations():
                parent = self.load_model_record_from_repository(rel)
                edges.append((mr.package_name(), parent.package_name()))
                find_parents(parent, indent = f'{indent}  ')
        find_parents(model_record)
        nodes = set([model_record.package_name()])
        for A,B in edges:
            nodes.add(A)
            nodes.add(B)
        return nodes, edges

    def load_modelrecord_yaml(self, pkg_query:str):
        yml_path = self.find_in_repo(pkg_query)        
        return self.merge_yml_modelrecords(yml_path)
    
    def merge_yml_modelrecords(self, yml_path:str):
        base_conf = OmegaConf.load(yml_path)

        relation_confs = [base_conf]

        if base_conf.mr.get('relations'):
            if base_conf.mr.relations.get('upstream'):
                for relation in base_conf.mr.relations.upstream:
                    relation_confs.append(OmegaConf.load(self.find_in_repo(relation)))

        yml = OmegaConf.unsafe_merge(*relation_confs[::-1])
        return yml

    def _load_model_record_from_path(self, path, pkg_name=None, version=None):
        yml = self.merge_yml_modelrecords(path)
        yml.mr.pkg = dict(
            name = pkg_name,
            version = str(version),
            path = path,
        )
        return ModelRecord(yml)
    
    def load_model_record_from_repository(self, pkg_query):
        parsed = self.pkg_parser.parse_pkg_version_query(pkg_query)
        yml_path = self.find_in_repo(pkg_query)
        return self._load_model_record_from_path(yml_path, pkg_name=parsed['pkg'], version=parsed['version'])

    # Download and update 
    def update_card_attrs(self, pkg, attrs):
        yml = self.load_modelrecord_yaml(pkg)
        for key, answer in attrs.items():
            OmegaConf.update(yml, key, answer, force_add=True)
        
        with open(self.find_in_repo(pkg)) as fp:
            OmegaConf.save(config=yml, f=fp.name)

    def download_and_process_refs(self, pkg:str):
        refs = self.load_modelrecord_yaml(pkg).mr.metadata.refs

        ref_path = f'{self.base_repo_path}/_refs/{pkg}'
        Path(f'{ref_path}').mkdir(parents=True, exist_ok=True)
        
        text_files = content_extract_text(refs, ref_path)
        return text_files