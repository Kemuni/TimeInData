
class APIError(Exception):
    """ Exception raised by API or APIParser """
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API Error [{code}]: {message}")
