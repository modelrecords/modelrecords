from omegaconf import OmegaConf
import semantic_version as semver
import re
import os
import operator
import requests
import mimetypes
import PyPDF2
from pathlib import Path
from importlib import resources
from modelrecords.modelrecord import ModelRecord 

#BASE_REPO_PATH = 'repository'
BASE_REPO_PATH = f'{resources.files('modelrecords')}/repository'
RESERVED_FOLDERS = ['_refs']

def download_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def detect_format(url, content):
    content_type = mimetypes.guess_type(url)
    if content_type[0]:
        return content_type[0].split('/')[1]
    else:
        return url.split('.')[-1].lower()


class Repository:
    def __init__(self, base_repo_path=BASE_REPO_PATH):
        self.base_repo_path = base_repo_path

    def parse_card_relation(self, card:str):
        operand = None
        try:
            package, version = re.split('>=|==|<=|-', card)
        except:
            package = card
            version = get_latest_semver(self.modelrecord_folder(package))
            return package, semver.Version(version), operand
        if '>=' in card:
            operand = operator.ge
        if '<=' in card:
            operand = operator.le
        if '==' in card:
            operand = operator.eq
        return package, semver.Version(version), operand

    def find_card_in_repo(self, card_relation:str):
        
        pkg, version, operand = self.parse_card_relation(card_relation)
        basepath = f'{self.base_repo_path}/{pkg}'
        # if the operand is None, then we have nothing to compare, so just grab the package
        if operand is None:
            return f'{basepath}/{pkg}-{version}.yaml'
        
        for candidate in sorted(os.listdir(basepath))[::-1]:
            _, candidate_version, _ = self.parse_card_relation(candidate.replace('.yaml',''))
            if operand(version , candidate_version):
                return f'{basepath}/{candidate}'
        raise f"No card found: {card_relation}"

    def download_and_process_refs(self, pkg:str):
        refs = self.load_modelrecord_yaml(pkg).mr.metadata.refs

        ref_path = f'{self.base_repo_path}/_refs/{pkg}'
        Path(f'{ref_path}').mkdir(parents=True, exist_ok=True)
        
        text_files = []
        
        for idx, url in enumerate(refs):
            content = download_url(url)
            if content:
                format = detect_format(url, content)
                file_path = None
                if format == 'pdf':
                    file_path = f'{ref_path}/{idx:03}.{format}'
                
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    reader = PyPDF2.PdfReader(file_path)
                    all_text = ''
                    for page in reader.pages:
                        all_text += page.extract_text()
                    
                    file_path = f'{file_path}.txt'
                    with open(file_path, 'w') as f:
                        f.writelines(all_text)
                elif format in ['html', 'htm']:    
                    file_path = f'{ref_path}/{idx:03}.{format}.txt'
                    with open(file_path, 'wb') as f:
                        f.write(content)
                elif format in ['md', 'txt']:
                    file_path = f'{ref_path}/{idx:03}.{format}.txt'
                    with open(file_path, 'wb') as f:
                        f.write(content)
                else:
                    print("Format could not be determined.")
                
                if file_path:
                    text_files.append(file_path)
        return text_files
    
    def all_packages(self):
        pkgs = [d for d in os.listdir(self.base_repo_path) if d not in RESERVED_FOLDERS]
        return pkgs

    def update_card_attrs(self, pkg, attrs):
        yml = self.load_modelrecord_yaml(pkg)
        for key, answer in attrs.items():
            OmegaConf.update(yml, key, answer, force_add=True)
        
        with open(self.modelrecord_yaml_path(pkg)) as fp:
            OmegaConf.save(config=yml, f=fp.name)

    def modelrecord_folder(self, pkg:str):
        return f'{self.base_repo_path}/{pkg}'

    def modelrecord_yaml_path(self, card:str):
        card_split = card.rsplit('-', 1)
        if len(card_split) == 2:
            pkg, version = card_split
            if not is_semver(version):
                version = get_latest_semver(self.modelrecord_folder(pkg))
                pkg = f'{card}'
                card = f'{pkg}-{version}'
        else:
            pkg = card_split[0]
            version = get_latest_semver(self.modelrecord_folder(pkg))
            card = f'{pkg}-{version}'
        return f'{self.modelrecord_folder(pkg)}/{card}.yaml'

    def load_modelrecord_yaml(self, card:str):
        yml_path = self.modelrecord_yaml_path(card)
        return self.merge_yml_modelrecords(yml_path)
    
    def merge_yml_modelrecords(self, yml_path:str):
        base_conf = OmegaConf.load(yml_path)

        relation_confs = [base_conf]

        if base_conf.mr.get('relations'):
            if base_conf.mr.relations.get('upstream'):
                for relation in base_conf.mr.relations.upstream:
                    relation_confs.append(OmegaConf.load(self.find_card_in_repo(relation)))

        return OmegaConf.unsafe_merge(*relation_confs[::-1])

    def load_model_record_from_path(self, path):
        yml = self.merge_yml_modelrecords(path)
    
        return ModelRecord(yml)
    
    def load_model_record_from_repository(self, pkg):
        yml_path = self.modelrecord_yaml_path(pkg)
        
        return self.load_model_record_from_path(yml_path)

def is_semver(version):
    # Regex to validate Semantic Versioning
    semver_regex = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    # Match the version string against the regex
    return bool(re.match(semver_regex, version))

def get_latest_semver(folder_path):
    
    semver_regex = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    max_version = None

    # Iterate over all files in the given folder
    for filename in os.listdir(folder_path):
        file_version = filename.rsplit('-', 1)[-1].split('.yaml')[0]
        match = re.match(semver_regex, file_version)
        if match:
            # Extract the semver part and parse it
            current_version = semver.Version(file_version)
            if max_version is None or current_version > max_version:
                max_version = current_version

    # Return the maximum version found, or None if no valid semver files were found
    return str(max_version) if max_version else None