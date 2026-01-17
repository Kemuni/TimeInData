export const baseURL: string = import.meta.env.VITE_API_DOMAIN!;

export class APIEndpointsUrls {
  public static GetUserLastActivity = (): string => `${baseURL}/user/activities/last`;
  public static PostNewUserActivities = (): string => `${baseURL}/user/activities`;
  public static GetClosestActivityMissingSlots = (): string => `${baseURL}/user/activities/missing_slots/closest`;
}
