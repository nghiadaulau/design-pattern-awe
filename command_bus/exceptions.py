class MissingHandler(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class OverWritingHandler(Exception):
    def __init__(self, message: str):
        super().__init__(message)
