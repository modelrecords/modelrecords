import semantic_version as semver # type: ignore
import re
import os
import operator
from modelrecords.utils import get_latest_semver, is_semver
from typing import Dict, Optional

class PackageParser:
    CHAR_DIVIDER = '-'
    DEFAULT_VERSION = '1.0.0'
    VERSION_OPERATORS_REGEX = re.compile(r'(>=|==|<=)')

    def __init__(self, base_repo_path: str):
        self.base_repo_path = os.path.normpath(base_repo_path)
    
    def modelrecord_folder(self, pkg: str) -> str:
        """
        Returns the full path to the model record folder for a given package.
        """
        return os.path.join(self.base_repo_path, pkg)
    
    def parse_version_yml_path(self, yml_path:str) -> semver.Version:
        return semver.Version(yml_path.rsplit(self.CHAR_DIVIDER, 1)[1].rsplit('.', 1)[0])

    def parse_pkg_name_yml_path(self, yml_path:str) -> str:
        return yml_path.replace(self.base_repo_path, '').rsplit(self.CHAR_DIVIDER)[0] 

    def parse_pkg_folder(self, pkg_version: str) -> str:
        """
        Parses the package version and returns the appropriate model record folder.
        """
        pkg_version = self._split_pkg_version(pkg_version)
        
        if self.CHAR_DIVIDER in pkg_version:
            candidate_pkg, candidate_version = pkg_version.rsplit(self.CHAR_DIVIDER, 1)
            if is_semver(candidate_version):
                return self.modelrecord_folder(candidate_pkg)
            else:
                return self.modelrecord_folder(pkg_version)    
        else:
            return self.modelrecord_folder(pkg_version)

    def parse_pkg_version(self, pkg_version: str, set_default_version: bool = True) -> Dict[str, Optional[semver.Version]]:
        version = self.DEFAULT_VERSION if set_default_version else None
        pkg = pkg_version

        if self.CHAR_DIVIDER in pkg_version:
            candidate_pkg, candidate_version = pkg_version.rsplit(self.CHAR_DIVIDER, 1)
            if is_semver(candidate_version):
                version = candidate_version
                pkg = candidate_pkg

        return {
            'pkg': pkg,
            'version': semver.Version(version) if version else None
        }
        
    def parse_pkg_version_query(self, pkg_version_query: str) -> Dict[str, object]:
        """
        Expects pkg_version_query to be in {pkg}{operand}{version} format.
        """
        pkg_folder = self.parse_pkg_folder(pkg_version_query)
        pkg_version = self.parse_pkg_version(pkg_version_query, set_default_version=False)
        package = pkg_version['pkg']
        operand = operator.eq

        if pkg_version['version'] is None:
            try:
                package, version_str = re.split(r'>=|==|<=', pkg_version_query)
                version = semver.Version(version_str)
                operand = self._get_operand(pkg_version_query)
            except:
                version = semver.Version(get_latest_semver(pkg_folder))
        else:
            version = pkg_version['version']

        return {'pkg': package, 'version': version, 'operand': operand}
    
    def _get_operand(self, query: str) -> operator:
        """
        Determines the comparison operand based on the query string.
        """
        if '>=' in query:
            return operator.ge
        elif '<=' in query:
            return operator.le
        elif '==' in query:
            return operator.eq
        else:
            return operator.eq

    def _split_pkg_version(self, pkg_version: str) -> str:
        """
        Splits the package version string by supported version operators and returns the package part.
        """
        pkg_query_split = self.VERSION_OPERATORS_REGEX.split(pkg_version)
        if len(pkg_query_split) > 1:
            return pkg_query_split[0]
        return pkg_version
