from planecards.types import PCBoolean, PCString, PCEnum
class Survey:
    """
    A base class representing a survey.

    Attributes:
        score (int): The score of the survey.
        answers (dict): A dictionary containing survey answers.
    """

    def __init__(self, question_answers):
        """
        Initializes a Survey object.

        Args:
            question_answers (list): A list of dictionaries containing question-answer pairs.
        """
        self.score = 0
        self.answers = question_answers

class FMTI2023(Survey):
    """
    A class representing the FMTI 2023 survey.
    Inherits from Survey.

    Attributes:
        QUESTION_SET (list): A list containing the question set for the survey.
        name (str): The model name extracted from survey answers.
    """

    QUESTION_SET = ['model_size', 'model_name']

    QUESTION_SET = [{
        'redteam': PCBoolean,
        'model_name': PCString,
        'model_size': PCEnum(['<400M', '400M-1B', '1B+']),
    }]


    def name(self):
        return 'FMTI - 2023'

    def parse(self):
        """
        Parses the survey answers.
        """
        # validation, checking, etc.
        self.model_name = self.answers['model_name']

        if self.answers['model_size'] == '400M':
            self.score += 1

        # support for calling out to a magical LLM that can read the project repo and be asked questions

    def result(self):
        return f"FMTI -- {self.model_name} is the model name, and your model size is big! {self.score}"
