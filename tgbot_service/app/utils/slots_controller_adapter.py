from aiogram_dialog import DialogManager

from app.exceptions import ManagerDialogDoesNotHaveKeyException, ManagerDialogAlreadyHasKeyException
from app.types import ActivitySlot, ActivitySlotsStore
from app.utils.activity_slots_controller import ActivitySlotsController


class ActivitySlotsToAiogramDialogAdapter:
    """ Adapter for activity slots controller to fsm storage """
    ACTIVITY_SLOTS_STORE_FSM_ID: str = "activity_slots_store"

    @classmethod
    def add_controller_to_dialog_data(
            cls, activity_slots_controller: ActivitySlotsController, dialog_manager: DialogManager
    ) -> None:
        if cls.ACTIVITY_SLOTS_STORE_FSM_ID in dialog_manager.dialog_data:
            raise ManagerDialogAlreadyHasKeyException(
                f'Failed to add activity slots data in `dialog_manager.dialog_data`: Already has key "{ActivitySlotsStore}"'
            )
        slots_store = activity_slots_controller.get_slots_store()
        json_slots_store = {local_hour: slot.model_dump(mode='json') for local_hour, slot in slots_store.items()}
        dialog_manager.dialog_data[cls.ACTIVITY_SLOTS_STORE_FSM_ID] = json_slots_store

    @classmethod
    def get_controller_from_dialog_data(cls, dialog_manager: DialogManager) -> ActivitySlotsController:
        if cls.ACTIVITY_SLOTS_STORE_FSM_ID not in dialog_manager.dialog_data:
            raise ManagerDialogDoesNotHaveKeyException(
                f'Failed to get activity slots data from dialog_manager.dialog_data: No key "{ActivitySlotsStore}"'
            )

        json_slots_store = dialog_manager.dialog_data[cls.ACTIVITY_SLOTS_STORE_FSM_ID]
        slots_store = {
            int(local_hour): ActivitySlot.model_validate(json_slot)
            for local_hour, json_slot in json_slots_store.items()
        }

        return ActivitySlotsController(activity_slots_store=slots_store)

