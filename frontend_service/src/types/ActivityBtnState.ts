import { ActivityType } from "./ActivityType.ts";


export default interface ActivityBtnState {
  date: Date,
  activity?: ActivityType | undefined,
  isSelected?: boolean | undefined,
}
