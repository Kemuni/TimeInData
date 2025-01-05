import { ActivityType } from "./ActivityType.ts";


export default interface ActivityBtnState {
  hour: number,
  activity?: ActivityType | undefined,
  isSelected?: boolean | undefined,
}
