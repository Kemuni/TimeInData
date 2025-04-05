import {useEffect, useState} from "react";
import {APIEndpointsUrls} from "@/services/api-urls";
import axios from "axios";
import Activity from "@/types/Activity";
import {ActivityType} from "@/types/ActivityType.ts";
import ActivityState from "@/types/ActivityState.ts";

interface ResponseActivity {
  id: number,
  time: string
  activity: ActivityType,
}


export const useGetLastUserActivity = (userId: number) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastActivity, setLastActivity] = useState<Activity|null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      await axios.get<ResponseActivity | null>(
        APIEndpointsUrls.GetUserLastActivity(userId), {
          headers: {
            "Content-Type": "application/json",
          },
          timeout: 5000
        }
      )
      .then(({ data }) => {
        if (data !== null) setLastActivity({...data, time: new Date(data.time)});
        setIsLoading(false);
      })
      .catch((e) => {
        setError(e.toString());
        setIsLoading(false);
        console.log(e);
      });
    }

    fetchData();
  }, []);

  return { lastActivity, isLoading, error };
}

export const useCreateNewActivities = (userId: number): [(activities: ActivityState[]) => Promise<void>, boolean, string] => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const createNewActivities = async (activities: ActivityState[]): Promise<void> => {
    setIsLoading(true);
    setError('')

    const data = {
      activities: activities.map(
        (item) => {
          const keys = Object.values(ActivityType);
          return {type: keys.indexOf(item.activity) + 1, time: item.date.toISOString()}
        }
      )
    }

    await axios.post(
      APIEndpointsUrls.PostNewUserActivities(userId),
      data,
      {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 8000
      }
    )
      .then(() => {
        setIsLoading(false);
        console.log('SUCCESS');
      })
      .catch((e) => {
        setError(e.toString());
        setIsLoading(false);
        console.log(e);
      });
  }

  return [ createNewActivities, isLoading, error ];
}
