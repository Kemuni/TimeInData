
class ActivitySlotsAdapterException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"ActivitySlotsAdapter Error: {message}")


class ManagerDialogAlreadyHasKeyException(ActivitySlotsAdapterException):
    def __init__(
            self,
            message: str = "Failed to add activity slots data in dialog_manager.dialog_data. Already has key!",
    ):
        super().__init__(message=message)


class ManagerDialogDoesNotHaveKeyException(ActivitySlotsAdapterException):
    def __init__(
            self,
            message: str = "Failed to get activity slots data from dialog_manager.dialog_data. No key!",
    ):
        super().__init__(message=message)
