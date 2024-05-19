
class ModelRecordType:
    """
    A base class representing a plane card type.
    """
    pass

class MREnum(ModelRecordType):
    """
    A class representing an enumerated plane card type.

    Attributes:
        options (list): A list of options for the enumerated type.
    """

    def __init__(self, options):
        """
        Initializes a MREnum object.

        Args:
            options (list): A list of options for the enumerated type.
        """
        self.options = options

class MRString(ModelRecordType):
    """
    A class representing a string plane card type.

    Attributes:
        options (list): A list of options for the string type.
    """

    def __init__(self, options):
        """
        Initializes a MRString object.

        Args:
            options (list): A list of options for the string type.
        """
        self.options = options

class MRBoolean(ModelRecordType):
    """
    A class representing a boolean plane card type.

    Attributes:
        options (list): A list of options for the boolean type.
    """

    def __init__(self, options):
        """
        Initializes a MRBoolean object.

        Args:
            options (list): A list of options for the boolean type.
        """
        self.options = options

