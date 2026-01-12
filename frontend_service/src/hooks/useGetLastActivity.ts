import {usersApi} from "@/services";
import {useApiQuery} from "@/hooks";
import {ActivityType} from "@/types";

export interface LastActivity {
  id: number;
  type: ActivityType;
  utc_date: Date;
  utc_hour: number;
}

export function useGetLastActivity(userId?: number) {
  return useApiQuery<LastActivity | null>({
    queryFn: async () => {
      if (!userId) throw new Error('User ID is required');
      const response = await usersApi.getLastActivity(userId);

      if (!response || !response.success || !response.data) return null;
      const data = response.data;

      return {
        id: data.id,
        type: data.type as ActivityType,
        utc_date: new Date(data.utc_date),
        utc_hour: Number(data.utc_hour),
      };
    },
    enabled: !!userId,
  });
}
