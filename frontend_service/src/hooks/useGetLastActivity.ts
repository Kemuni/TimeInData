import {usersApi} from "@/services";
import {useApiQuery} from "@/hooks";
import {ActivityType} from "@/types";
import {useRawInitData} from "@tma.js/sdk-react";

export interface LastActivity {
  id: number;
  type: ActivityType;
  utc_date: Date;
  utc_hour: number;
}

export function useGetLastActivity() {
  const rawInitData = useRawInitData();
  return useApiQuery<LastActivity | null>({
    queryFn: async () => {
      if (!rawInitData) throw new Error('rawInitData is required for authentication');
      const response = await usersApi.getLastActivity(rawInitData);

      if (!response || !response.success || !response.data) return null;
      const data = response.data;

      return {
        id: data.id,
        type: data.type as ActivityType,
        utc_date: new Date(data.utc_date),
        utc_hour: Number(data.utc_hour),
      };
    },
    enabled: !!rawInitData,
  });
}
