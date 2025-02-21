import { ActivityType } from "./ActivityType.ts";


export default interface ActivityState {
  date: Date,
  activity?: ActivityType | undefined,
}
