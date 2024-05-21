import unittest

from modelrecords import repository

class TestRepository(unittest.TestCase):
    def test_list_all_packages(self):
        repo = repository.Repository()
        pkgs = repo.all_packages()
        assert len(pkgs) > 10
        assert '_refs' not in pkgs

if __name__ == '__main__':
    unittest.main()