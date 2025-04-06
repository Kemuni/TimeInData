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


interface UseGetLastUserActivityResult {
  lastActivity: Activity | null;
  isLoading: boolean;
  error: string;
}


export const useGetLastUserActivity = (
  userId?: number
): UseGetLastUserActivityResult => {
  const [state, setState] = useState<UseGetLastUserActivityResult>({
    lastActivity: null,
    isLoading: false,
    error: "",
  });

  useEffect(() => {
    if (!userId) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, isLoading: true, error: "" }));

      try {
        const { data } = await axios.get<ResponseActivity | null>(
          APIEndpointsUrls.GetUserLastActivity(userId),
          {
            headers: { "Content-Type": "application/json" },
            timeout: 5000,
          }
        );

        setState({
          lastActivity: data ? { ...data, time: new Date(data.time) } : null,
          isLoading: false,
          error: "",
        });
      } catch (e) {
        setState({
          lastActivity: null,
          isLoading: false,
          error: e instanceof Error ? e.message : "Unknown error",
        });
      }
    }

    fetchData();
  }, [userId]);

  return state;
}


interface UseCreateNewActivitiesResult {
  createNewActivities: (activities: ActivityState[]) => Promise<void>;
  isLoading: boolean;
  error: string;
}


export const useCreateNewActivities = (
  userId?: number
): UseCreateNewActivitiesResult => {
  const [state, setState] = useState<Omit<UseCreateNewActivitiesResult, "createNewActivities">>({
    isLoading: false,
    error: "",
  });

  const createNewActivities = async (activities: ActivityState[]) => {
    if (!userId) {
      setState((prev) => ({ ...prev, error: "User ID is missing" }));
      return;
    }

    setState({ isLoading: true, error: "" });

    try {
      const data = activities.map((item) => ({
        type: Object.values(ActivityType).indexOf(item.activity) + 1,
        time: item.date.toISOString(),
      }));

      await axios.post(APIEndpointsUrls.PostNewUserActivities(userId), { activities: data }, {
        headers: { "Content-Type": "application/json" },
        timeout: 8000,
      });

      setState({ isLoading: false, error: "" });
    } catch (e) {
      setState({
        isLoading: false,
        error: e instanceof Error ? e.message : "Failed to create activities",
      });
    }
  }

  return { ...state, createNewActivities };
}
