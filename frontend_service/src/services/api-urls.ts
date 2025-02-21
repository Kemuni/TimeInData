const baseURL: string = import.meta.env.VITE_API_API_DOMAIN!;

export class APIEndpointsUrls {
  public static GetUserLastActivity = (user_id: number): string => `${baseURL}/users/${user_id}/activities/last`;
}
