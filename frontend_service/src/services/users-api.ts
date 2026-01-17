import { apiClient } from './api-client';
import {APIEndpointsUrls} from "@/services/api-urls.ts";

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
}

export interface LastActivityData {
  id: number;
  type: string;
  utc_date: string;
  utc_hour: number;
}

export interface LastActivityResponse extends ApiResponse<LastActivityData> {}

export interface CreateActivitiesPayload {
  activities: Array<{
    type: string;
    utc_date: string;
    utc_hour: number;
  }>;
}

export interface MissingActivitySlotsData {
  has_missing_slots: boolean;
  date_range?: {from_date: string, to_date: string}
  missing_slots?: Array<{utc_date: string, utc_hour: number}>
  total_missing: number;
}

export interface MissingActivitySlotsResponse extends ApiResponse<MissingActivitySlotsData> {}

export const usersApi = {
  getLastActivity: async (rawInitData: string) => {
    const { data } = await apiClient.get<LastActivityResponse | null>(
      APIEndpointsUrls.GetUserLastActivity(),
      {
        headers: { 'Authorization': `TMA ${rawInitData}` },
      }
    );
    return data;
  },

  getClosestMissingActivitySlots: async (rawInitData: string) => {
    const { data } = await apiClient.get<MissingActivitySlotsResponse>(
      APIEndpointsUrls.GetClosestActivityMissingSlots(),
      {
        headers: { 'Authorization': `TMA ${rawInitData}` },
      }
    )
    return data;
  },

  createActivities: async (payload: CreateActivitiesPayload, rawInitData: string) => {
    await apiClient.post(
      APIEndpointsUrls.PostNewUserActivities(),
      payload,
      {
        headers: { 'Authorization': `TMA ${rawInitData}` },
      }
    );
  },
};
