export const baseURL: string = import.meta.env.VITE_API_DOMAIN!;

export class APIEndpointsUrls {
  public static GetUserLastActivity = (userId: number): string => `${baseURL}/users/${userId}/activities/last`;
  public static PostNewUserActivities = (userId: number): string => `${baseURL}/users/${userId}/activities`;
  public static GetClosestActivityMissingSlots = (userId: number): string => `${baseURL}/users/${userId}/activities/missing_slots/closest`;
}
