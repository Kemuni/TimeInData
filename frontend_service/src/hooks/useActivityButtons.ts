import {ActivityType, ActivityButtonStates} from "@/types";
import {useEffect, useState} from "react";

interface UtcActivitySlot {
  utcDate: Date;
  utcHour: number;
}

interface UseActivityButtonsProps {
  utcMissingActivitySlots?: Array<UtcActivitySlot>;
}

export interface UseActivityButtonsReturn {
  activityButtonStates: ActivityButtonStates;

  /**
   * Toggle activity button.
   * @param index - Index of hour activity button in `hourActivityBtnState`.
   */
  toggleActivityBtn: (index: number) => void;

  /**
   * Change activity type of toggled activity buttons.
   * @param newActivity - New activity type.
   */
  changeActivityOfToggledBtns: (newActivity: ActivityType) => void;

  /**
   * Check if hour activity button is toggled.
   * @param index - Index of hour activity button in `hourActivityBtnState`.
   */
  isActivityBtnToggled: (index: number) => boolean;
}

/**
 * Hook to interact with hour activities buttons.
 * @param utcDatesToFill - Array of UTC dates to fill.
 */
export function useActivityButtons(
  {
    utcMissingActivitySlots,
  }: UseActivityButtonsProps): UseActivityButtonsReturn
{
  const [activityButtonStates, setActivityButtonStates] = useState<ActivityButtonStates>([]);

  // Define initial activities state for buttons
  useEffect(() => {
    if (!utcMissingActivitySlots) return;
    const activities: ActivityButtonStates = [];
    const tzOffsetHours = new Date().getTimezoneOffset() / 60 * -1;  // Time zone Offset in hours
    utcMissingActivitySlots
      .sort(
        (a, b) =>
          getDateFromUtcDateAndHour(a).getTime() - getDateFromUtcDateAndHour(b).getTime()
        )
      .forEach((item, index) => activities.push({
        index: index,
        utc_date: new Date(item.utcDate),
        utc_hour: item.utcHour,
        local_date: clearHours(getDateFromUtcDateAndHour({...item, tzOffsetHours: tzOffsetHours})),
        local_hour: (item.utcHour + tzOffsetHours) % 24,
        activity: undefined,
      }));
    setActivityButtonStates(activities);
  }, [utcMissingActivitySlots]);

  const [toggledButtonsIndexes, setToggledButtonsIndexes] = useState<Set<number>>(new Set<number>());

  const toggleActivityBtn = (index: number) => {
    const updateData = new Set(toggledButtonsIndexes);
    if (toggledButtonsIndexes.has(index)) updateData.delete(index);
    else updateData.add(index);
    setToggledButtonsIndexes(updateData);
  }

  const changeActivityOfToggledBtns = (newActivity: ActivityType) => {
    const updateData = Array.from(activityButtonStates);
    toggledButtonsIndexes.forEach((btnIndex) => {
      updateData[btnIndex].activity = newActivity;
    })
    setToggledButtonsIndexes(new Set<number>());
    setActivityButtonStates(updateData);
  }

  const isActivityBtnToggled = (index: number) => toggledButtonsIndexes.has(index);

  return {
    activityButtonStates,
    toggleActivityBtn,
    changeActivityOfToggledBtns,
    isActivityBtnToggled,
  }
}


function getDateFromUtcDateAndHour({
     utcDate,
     utcHour,
     tzOffsetHours = 0
   }: UtcActivitySlot & {tzOffsetHours?: number}
) {
  const utcDateCopy = new Date(utcDate);
  utcDateCopy.setHours(utcHour)
  return new Date(utcDateCopy.getTime() + tzOffsetHours * 60 * 60 * 1_000);
}


function clearHours(date: Date) {
  const newDate = new Date(date);
  newDate.setHours(0, 0, 0, 0);
  return newDate;
}
