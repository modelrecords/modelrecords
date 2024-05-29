import unittest
import semantic_version as semver
from modelrecords import repository
import operator

def run_assertions(fun, cases):
    for val, assertion in cases.items():
        try:
            assert fun(val) == assertion
        except:
            raise Exception(f'got: "{fun(val)}" expected: "{assertion}"')


class TestRepository(unittest.TestCase):
    def test_list_all_packages(self):
        repo = repository.Repository()
        pkgs = repo.all_packages()
        assert len(pkgs) > 10
        assert '_refs' not in pkgs


    def test_parse_pkg_name_to_pkg_folder(self):
        pkg_parser = repository.PackageParser('myfolder/')
        cases = {
            'abc': 'myfolder/abc',
            'abc-1b': 'myfolder/abc-1b',
            'abc-aa-aa': 'myfolder/abc-aa-aa',
            'abc-1b-1.2.0': 'myfolder/abc-1b',
            'abc-1b>=1.2.0': 'myfolder/abc-1b',
            'abc-1b==1.2.0': 'myfolder/abc-1b',
            'abc-1b<=1.2.0': 'myfolder/abc-1b'
        }
        fun = lambda x : pkg_parser.parse_pkg_folder(x)
        run_assertions(fun, cases)
        
    def test_parse_pkg_name_to_pkg_version(self):
        pkg_parser = repository.PackageParser('myfolder/')
        cases = {
            'abc': {'pkg': 'abc', 'version': semver.Version('1.0.0')},
            'abc-1b': {'pkg': 'abc-1b', 'version':semver.Version('1.0.0')},
            'abc-aa-aa': {'pkg': 'abc-aa-aa', 'version':semver.Version('1.0.0')},
            'abc-1b-1.2.0': {'pkg': 'abc-1b', 'version':semver.Version('1.2.0')},
        }
        fun = lambda x : pkg_parser.parse_pkg_version(x)
        run_assertions(fun, cases)

    def test_parse_pkg_version_query(self):
        pkg_parser = repository.PackageParser('modelrecords/repository/')
        v1 = semver.Version('1.0.0')
        cases = {
            'bloomz-7b1-1.0.0': {'pkg': 'bloomz-7b1', 'version': v1, 'operand': operator.eq },
            'bloomz-7b1': {'pkg': 'bloomz-7b1', 'version': v1, 'operand': operator.eq },
            'bloomz-7b1>=1.0.0': {'pkg': 'bloomz-7b1', 'version': v1, 'operand': operator.ge },
            'bloomz-7b1==1.0.0': {'pkg': 'bloomz-7b1', 'version': v1, 'operand': operator.eq },
            'bloomz-7b1<=1.0.0': {'pkg': 'bloomz-7b1', 'version': v1, 'operand': operator.le },
            'test==1.2.0': {'pkg': 'test', 'version': semver.Version('1.2.0'), 'operand': operator.eq },
            'test==1.0.0': {'pkg': 'test', 'version': semver.Version('1.0.0'), 'operand': operator.eq },
            'test<=1.0.0': {'pkg': 'test', 'version': semver.Version('1.0.0'), 'operand': operator.le },
            'test>=1.1.0': {'pkg': 'test', 'version': semver.Version('1.1.0'), 'operand': operator.ge },
        }
        fun = lambda x : pkg_parser.parse_pkg_version_query(x)
        run_assertions(fun, cases)
    
    def test_parse_repo_requirement(self):
        repo = repository.Repository()

        mr = repo.find('llama2>=1.0.0')
        a = repo.find('llama2==1.0.0')
        b = repo.find('llama2-1.0.0')
        c = repo.find('llama2<=1.0.0')
        d = repo.find('llama2')
        assert mr.model_name == a.model_name
        assert mr.model_name == b.model_name
        assert mr.model_name == c.model_name
        assert mr.model_name == d.model_name

    def test_parse_repo_with_operand(self):
        repo = repository.Repository()
        a = repo.find('test==1.2.0')
        b = repo.find('test>=1.1.0')
        assert a.model_name == b.model_name

        a = repo.find('test==1.0.0')
        b = repo.find('test<=1.1.0')
        assert a.pkg.version == b.pkg.version
        assert '1.0.0' == b.pkg.version
if __name__ == '__main__':
    unittest.main()