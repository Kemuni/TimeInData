import {useEffect, useState} from "react";
import {APIEndpointsUrls} from "@/services/api-urls";
import axios from "axios";
import Activity from "@/types/Activity";
import {ActivityType} from "@/types/ActivityType.ts";

interface ResponseActivity {
  id: number,
  time: string
  activity: ActivityType,
}


export const useGetLastUserActivity = (user_id: number) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastActivity, setLastActivity] = useState<Activity|undefined>(undefined);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      await axios.get<ResponseActivity>(
        APIEndpointsUrls.GetUserLastActivity(user_id), {
          headers: {
            "Content-Type": "application/json",
          },
          timeout: 5000
        }
      )
      .then(({ data }) => {
        setLastActivity({...data, time: new Date(data.time)});
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
