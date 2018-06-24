class ElementNotLocatedError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('No Slider Element Found')


class ParameterNotSetError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('Parameter(s) Not Input')


