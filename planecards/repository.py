from omegaconf import OmegaConf
import semantic_version as semver
import re
import os
import operator

BASE_REPO_PATH = 'repository'

class Repository:
    def __init__(self, base_repo_path=BASE_REPO_PATH):
        self.base_repo_path = base_repo_path

    def parse_card_relation(self, card:str):
        operand = None
        package, version = re.split('>=|==|<=|-', card)
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
        for candidate in sorted(os.listdir(basepath))[::-1]:
            _, candidate_version, _ = self.parse_card_relation(candidate.replace('.yaml',''))
            if operand(version , candidate_version):
                return f'{basepath}/{candidate}'
        raise f"No card found: {card_relation}"

    def load_plane_card_yaml(self, card:str):
        pkg = card.replace(card.split('-')[-1], '')[:-1]
        
        base_conf = OmegaConf.load(f'{self.base_repo_path}/{pkg}/{card}.yaml')

        relation_confs = [base_conf]

        if base_conf.pc.get('relations'):
            if base_conf.pc.relations.get('upstream'):
                for relation in base_conf.pc.relations.upstream:
                    #print(parse_card_relation(relation))
                    relation_confs.append(OmegaConf.load(self.find_card_in_repo(relation)))

        return OmegaConf.unsafe_merge(*relation_confs[::-1])