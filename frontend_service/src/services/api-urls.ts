const baseURL: string = import.meta.env.VITE_API_API_DOMAIN!;

export class APIEndpointsUrls {
  public static GetUserLastActivity = (userId: number): string => `${baseURL}/users/${userId}/activities/last`;
  public static PostNewUserActivities = (userId: number): string => `${baseURL}/users/${userId}/activities`;
}
