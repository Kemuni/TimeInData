import {useApiMutation} from "@/hooks";
import {ActivityType} from "@/types";
import {CreateActivitiesPayload, usersApi} from "@/services";

interface CreateActivityVariable {
  type: ActivityType;
  utc_date: Date;
  utc_hour: number;
}

interface CreateActivitiesVariables {
  userId: number;
  activities: CreateActivityVariable[];
}

export function useCreateActivities() {
  return useApiMutation<void, CreateActivitiesVariables>({
    mutationFn: async ({ userId, activities }) => {
      const payload: CreateActivitiesPayload = {
        activities: activities.map((item) => ({
          type: item.type.toString(),
          utc_date: getISOStringWithoutTimezone(item.utc_date),
          utc_hour: item.utc_hour,
        })),
      };

      await usersApi.createActivities(userId, payload);
    },
    onSuccess: () => {
      console.log('Activities created successfully');
    },
    onError: (error) => {
      console.error('Failed to create activities:', error);
    },
  });
}


function getISOStringWithoutTimezone(date: Date) {
  const monthStr = String(date.getMonth() + 1).padStart(2, '0');
  const dayStr = String(date.getDate()).padStart(2, '0');
  return `${date.getFullYear()}-${monthStr}-${dayStr}`;
}
