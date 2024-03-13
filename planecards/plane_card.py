from planecards.survey import FMTI2023


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

    def __init__(self, plane_card, model_name, locale=None):
        """
        Initializes a PlaneCard object.

        Args:
            plane_card (dict): A dictionary containing plane card attributes.
            model_name (str): The model name extracted from the plane card attributes.
            locale (str, optional): The locale to use for question text retrieval. Defaults to None.
        """
        self.plane_card_attrs = plane_card
        self.model_name = model_name
        self.locale = locale

    def parse(self):
        """
        Parses the plane card attributes and stores the parsed question sets.
        """
        self.question_sets_parsed = []
        for question_set in self.plane_card_attrs["question_sets"]:
            qs = self.QUESTION_SETS[question_set](
                self.plane_card_attrs["question_answers"],
                self.model_name,
            )
            qs.parse()
            self.question_sets_parsed.append(qs)

    def results(self):
        """
        Prints the parsed question sets.
        """
        return [(qsp.name(), qsp.result()) for qsp in self.question_sets_parsed]
