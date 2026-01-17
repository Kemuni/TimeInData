from datetime import datetime, time, timedelta
from typing import Optional, List, Any
from aiogram_dialog import DialogManager

from app.exceptions import (
    ActivitySlotsControllerInitException,
    NotFoundActivitySlotException,
    ActivitySlotAlreadyHasActivityException, ManagerDialogAlreadyHasKeyException, ManagerDialogDoesNotHaveKeyException,
)
from app.types import (
    ActivityTypes,
    MissingActivitySlot,
    ActivitySlot,
    ActivitySlotsFilterByLocalDate,
    ActivitySlotsStore,
)


class ActivitySlotsController:
    """ Controller for activity slots. Only 24 slots. """
    # Store of activity slots (local_hour -> activity slot)
    activity_slots_store: ActivitySlotsStore

    def __init__(
            self,
            utc_missing_slots: Optional[List[MissingActivitySlot]] = None,
            tz_delta: int = 0,
            activity_slots_store: Optional[ActivitySlotsStore] = None
    ):
        if utc_missing_slots is None and activity_slots_store is None:
            raise ActivitySlotsControllerInitException(
                "At least one of utc_missing_slots or activity_slots_store must be provided!"
            )
        if utc_missing_slots and activity_slots_store:
            raise ActivitySlotsControllerInitException(
                "Both utc_missing_slots and activity_slots_store cannot be provided!"
            )

        if activity_slots_store is not None:
            self.__init_by_activity_slots_store(activity_slots_store)
        else:
            self.__init_by_utc_missing_slots(utc_missing_slots, tz_delta)



    def __init_by_utc_missing_slots(
            self, utc_missing_slots: List[MissingActivitySlot], tz_delta: int
    ):
        """ Initialize controller by utc missing slots with tz_delta """
        if len(utc_missing_slots) > 24:
            raise ActivitySlotsControllerInitException("Too many missing slots!")
        if len(set(slot.utc_hour for slot in utc_missing_slots)) != len(utc_missing_slots):
            raise ActivitySlotsControllerInitException("Hour in slots must be unique!")

        self.activity_slots_store = self._parse_missing_slots_to_activity_slots_store(utc_missing_slots, tz_delta)

    def __init_by_activity_slots_store(self, activity_slots_store: ActivitySlotsStore):
        """ Initialize controller by activity slots store """
        self.activity_slots_store = activity_slots_store

    @staticmethod
    def _parse_missing_slots_to_activity_slots_store(
            utc_missing_slots: List[MissingActivitySlot], tz_delta: int
    ) -> dict[int, ActivitySlot]:
        """ Parse missing slots to activity slots store """
        activity_slots_store = {}
        for utc_slot in utc_missing_slots:
            utc_slot_datetime = datetime.combine(utc_slot.utc_date, time(hour=utc_slot.utc_hour))
            local_slot_datetime = utc_slot_datetime + timedelta(hours=tz_delta)

            activity_slots_store[local_slot_datetime.hour] = ActivitySlot(
                utc_hour=utc_slot.utc_hour,
                utc_date=utc_slot.utc_date,
                local_hour=local_slot_datetime.hour,
                local_date=local_slot_datetime.date(),
                activity_type=None,
            )

        return activity_slots_store


    def add_activity_slot(self, local_hour: int, activity: ActivityTypes):
        if local_hour not in self.activity_slots_store:
            raise NotFoundActivitySlotException()
        if self.activity_slots_store[local_hour].activity_type is not None:
            raise ActivitySlotAlreadyHasActivityException()
        self.activity_slots_store[local_hour].activity_type = activity

    def get_slots_filtered_by_date(self) -> List[ActivitySlotsFilterByLocalDate]:
        """ Get activity slots filtered by local date """
        filtered_slots = []

        filtered_slot: Optional[ActivitySlotsFilterByLocalDate] = None
        for activity_slot in self.activity_slots_store.values():
            if getattr(filtered_slot, 'local_date', None) != activity_slot.local_date:
                if filtered_slot is not None:
                    filtered_slots.append(filtered_slot)
                filtered_slot = ActivitySlotsFilterByLocalDate(
                    local_date=activity_slot.local_date, activity_slots=[activity_slot]
                )
            else:
                filtered_slot.activity_slots.append(activity_slot)
        filtered_slots.append(filtered_slot)

        return filtered_slots

    def has_all_slots_filled(self) -> bool:
        return all(slot.activity_type is not None for slot in self.activity_slots_store.values())

    def get_all_slots(self) -> List[ActivitySlot]:
        return list(self.activity_slots_store.values())

    def get_slots_store(self) -> ActivitySlotsStore:
        return self.activity_slots_store



