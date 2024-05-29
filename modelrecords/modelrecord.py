import datetime
from modelrecords.surveys.fmti2023 import FMTI2023
from collections.abc import MutableMapping
from modelrecords.package_parser import PackageParser


def flatten(dictionary, parent_key="", separator="."):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


class DotDict(dict):
    __delattr__ = dict.__delitem__
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, "keys"):
                value = DotDict(value)
            self[key] = value


class ModelRecord:
    """
    A class representing a plane card.

    Attributes:
        QUESTION_SETS (dict): A dictionary mapping plane card types to their respective question sets.
        params (dict): A dictionary containing plane card attributes.
        model_name (str): The model name extracted from the plane card attributes.
        locale (str): The locale used for question text retrieval.
        question_sets_parsed (list): A list to store parsed question sets.
    """

    QUESTION_SETS = {"fmti2023": FMTI2023}
    
    def __init__(self, modelrecord_params, locale=None):
        """
        Initializes a ModelRecord object.

        Args:
            modelrecord (dict): A dictionary containing plane card attributes.
            locale (str, optional): The locale to use for question text retrieval. Defaults to None.
        """
        self.params = DotDict(modelrecord_params)
        self.model_name = self.params.mr.metadata.name
        # TODO(someone): re-add the MR package name at some point.
        # self.pkg_name = self.params.mr.metadata.pkg_name 
        self.locale = locale
        self.parse()

    def parse(self):
        """
        Parses the plane card attributes and stores the parsed question sets.
        """
        self.question_sets_parsed = []
        if self.params["mr"].question_sets:
            for question_set in self.params["mr"].question_sets:
                qs = self.QUESTION_SETS[question_set](
                    flatten(self.params["mr"]),
                    self.model_name,
                )
                qs.parse()
                self.question_sets_parsed.append(qs)
        for k, v in self.params.mr.items():
            setattr(self, k, v)

    def results_as_dict(self):
        out = self.params
        today = datetime.datetime.today()
        out.last_updated = today.strftime("%a %b %y")
        for qsp in self.question_sets_parsed:
            out[f"result_{qsp.name()}"] = qsp.result()
        return out

    def results(self):
        """
        Prints the parsed question sets.
        """
        return [(qsp.name(), qsp.result()) for qsp in self.question_sets_parsed]

    def package_name(self):
        return self.params.mr.pkg.name
    
    def upstream_relations(self):
        if self.results_as_dict().mr.relations:
            if self.results_as_dict().mr.relations.upstream:
                return self.results_as_dict().mr.relations.upstream
        return []
    
    def upstream_relations_package(self):
        
        return [(PackageParser.VERSION_OPERATORS_REGEX.split(rel)[0], rel) for rel in self.upstream_relations()]