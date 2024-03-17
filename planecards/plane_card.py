import datetime
from planecards.survey import FMTI2023
from collections.abc import MutableMapping

def flatten(dictionary, parent_key='', separator='.'):
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
                if hasattr(value, 'keys'):
                    value = DotDict(value)
                self[key] = value

class PlaneCard:
    """
    A class representing a plane card.

    Attributes:
        QUESTION_SETS (dict): A dictionary mapping plane card types to their respective question sets.
        plane_card_attrs (dict): A dictionary containing plane card attributes.
        model_name (str): The model name extracted from the plane card attributes.
        locale (str): The locale used for question text retrieval.
        question_sets_parsed (list): A list to store parsed question sets.
    """

    QUESTION_SETS = {"fmti2023": FMTI2023}

    def __init__(self, plane_card, locale=None):
        """
        Initializes a PlaneCard object.

        Args:
            plane_card (dict): A dictionary containing plane card attributes.
            locale (str, optional): The locale to use for question text retrieval. Defaults to None.
        """
        self.plane_card_attrs = DotDict(plane_card)
        self.model_name = self.plane_card_attrs.pc.metadata.model_name
        self.locale = locale

    def parse(self):
        """
        Parses the plane card attributes and stores the parsed question sets.
        """
        self.question_sets_parsed = []
        for question_set in self.plane_card_attrs["pc"].question_sets:
            qs = self.QUESTION_SETS[question_set](
                flatten(self.plane_card_attrs["pc"]),
                self.model_name,
            )
            qs.parse()
            self.question_sets_parsed.append(qs)
    
    def results_as_dict(self):
        out = self.plane_card_attrs
        today = datetime.datetime.today()
        out.last_updated = today.strftime("%a %b %y")
        for qsp in self.question_sets_parsed:
            out[f'result_{qsp.name()}'] = qsp.result()
        return out
    
    def results(self):
        """
        Prints the parsed question sets.
        """
        return [(qsp.name(), qsp.result()) for qsp in self.question_sets_parsed]
