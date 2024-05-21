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


