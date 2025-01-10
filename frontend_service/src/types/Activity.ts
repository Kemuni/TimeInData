import { ActivityType } from "./ActivityType.ts";


export default interface Activity {
  id: number,
  time: Date,
  activity: ActivityType,
}
