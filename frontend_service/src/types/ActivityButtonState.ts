import { ActivityType } from "./ActivityType.ts";


export interface ActivityButtonState {
  index: number;
  utc_date: Date,
  utc_hour: number,
  local_date: Date,
  local_hour: number,
  activity?: ActivityType | undefined,
}

export type ActivityButtonStates = ActivityButtonState[];
