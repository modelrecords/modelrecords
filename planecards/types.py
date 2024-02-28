
class PlaneCardType:
    """
    A base class representing a plane card type.
    """
    pass

class PCEnum(PlaneCardType):
    """
    A class representing an enumerated plane card type.

    Attributes:
        options (list): A list of options for the enumerated type.
    """

    def __init__(self, options):
        """
        Initializes a PCEnum object.

        Args:
            options (list): A list of options for the enumerated type.
        """
        self.options = options

class PCString(PlaneCardType):
    """
    A class representing a string plane card type.

    Attributes:
        options (list): A list of options for the string type.
    """

    def __init__(self, options):
        """
        Initializes a PCString object.

        Args:
            options (list): A list of options for the string type.
        """
        self.options = options

class PCBoolean(PlaneCardType):
    """
    A class representing a boolean plane card type.

    Attributes:
        options (list): A list of options for the boolean type.
    """

    def __init__(self, options):
        """
        Initializes a PCBoolean object.

        Args:
            options (list): A list of options for the boolean type.
        """
        self.options = options

