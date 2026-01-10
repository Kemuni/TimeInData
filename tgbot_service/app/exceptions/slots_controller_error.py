
class ActivitySlotsControllerBaseException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Slots Controller Error: {message}")


class ActivitySlotsControllerInitException(ActivitySlotsControllerBaseException):
    def __init__(self, message: str):
        super().__init__(message=message)


class NotFoundActivitySlotException(ActivitySlotsControllerBaseException):
    def __init__(self, message: str = "Slot not found!"):
        super().__init__(message=message)


class ActivitySlotAlreadyHasActivityException(ActivitySlotsControllerBaseException):
    def __init__(self, message: str = "Slot already has activity!"):
        super().__init__(message=message)
