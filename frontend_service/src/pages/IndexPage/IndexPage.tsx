import {FC, useEffect, useReducer} from "react";
import {List, Placeholder, Subheadline,} from "@telegram-apps/telegram-ui";

import "./IndexPage.scss";
import {ActivitiesDateSelect} from "@/components/ActivitiesDateSelect.tsx";
import {ActivityTypesButtons} from "@/components/ActivityTypesButtons.tsx";
import {ActivityType} from "@/types/ActivityType.ts";
import {postEvent, retrieveLaunchParams} from "@telegram-apps/sdk-react";
import ActivityBtnState from "@/types/ActivityBtnState.ts";
import {Page} from "@/components/Page.tsx";
import {useGetLastUserActivity} from "@/hooks/activity.ts";

enum ActivityButtonActionType {
  TOGGLE = "toggle",
  CHANGE_ACTIVITY = "change_activity",
  FILL_ACTIVITIES = "fill_activities",
}

type ActivitiesState = ActivityBtnState[];

interface  ActivityButtonAction {
  type: ActivityButtonActionType
  activityIndex?: number
  newActivityType?: ActivityType
  newActivities?: ActivitiesState,
}

/**
 * Get activities that user have to fill, based on last filled activity
 * @param lastActivityUTCDate - Date of the last filled activity in UTC.
 * @return ActivitiesState - Activities state that user have to fill.
 */
function getActivitiesToFill(lastActivityUTCDate: Date | undefined): ActivitiesState {
  const OneHourInMs = 3_600_000;  // 60 * 60 * 1_000

  let currentDate: Date = new Date();
  currentDate = new Date(
    currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate(),
    currentDate.getHours(),
  )
  let lastActivityDate: Date;  // Date of last activity in User time zone or current date minus 7 hours
  if (lastActivityUTCDate !== undefined) {
    lastActivityDate = new Date(lastActivityUTCDate.getTime() + (-currentDate.getTimezoneOffset()) * 60_000);
  } else {
    lastActivityDate = new Date(currentDate.getTime() - 7 * OneHourInMs);
  }


  const diffMs: number = (currentDate.getTime() - lastActivityDate.getTime());
  let diffHours: number = Math.floor(diffMs / OneHourInMs) - 1;
  if (diffHours > 24) diffHours = 24;

  const activitiesStateToSet: ActivitiesState = [];
  for (let i: number = diffHours; i != 0; i--) {
    const msOffsetToActivityHour: number = i * OneHourInMs;
    activitiesStateToSet.push({date: new Date(currentDate.getTime() - msOffsetToActivityHour)})
  }
  return activitiesStateToSet;
}


export const IndexPage: FC = () => {
  const { initData } = retrieveLaunchParams();

  const { lastActivity, isLoading, error} = useGetLastUserActivity(initData?.user?.id!);

  useEffect(() => {
    postEvent(
    'web_app_setup_main_button',
    {
      is_visible: false,
      is_active: false,
      text: 'Save activities',
    });
  }, []);

  const initActivities: ActivitiesState = [];
  const [activitiesState, dispatchActivities] = useReducer(activitiesReducer, initActivities);

  useEffect(() => {
    if (isLoading || error !== '') return;
    dispatchActivities({
      type: ActivityButtonActionType.FILL_ACTIVITIES,
      newActivities: getActivitiesToFill(lastActivity?.time),
    });
  }, [isLoading]);

  function handleToggleHour(index: number) {
    dispatchActivities({
      type: ActivityButtonActionType.TOGGLE,
      activityIndex: index,
    });
  }

  function handleActivitySelect(activity: ActivityType) {
    dispatchActivities({
      type: ActivityButtonActionType.CHANGE_ACTIVITY,
      newActivityType: activity,
    });
  }

  const isStateReady = (!isLoading && error === '' && activitiesState.length !== 0);
  let placeholderHeader: string, placeholderDescription: string;
  if (isLoading) {
    placeholderHeader = 'Loading data...';
    placeholderDescription = 'Wait a little';
  } else if (error !== '') {
    placeholderHeader = "Some error occurs :(";
    placeholderDescription = "Try again later!";
  } else if (activitiesState.length === 0) {
    placeholderHeader = "All activities are set!";
    placeholderDescription = "You set all your activities, great job, buddy";
  } else {
    placeholderHeader = "Set your activities";
    placeholderDescription = "";
  }

  return (
    <Page back={false}>
      <List
        style={{
          backgroundColor: "var(--tgui--secondary_bg_color)",
          height: "100vh",
          width: "100vw",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
      }}
      >
        <div style={{maxWidth: "250px", margin: "0 auto"}}>
          <Placeholder
            header={placeholderHeader}
            description={placeholderDescription}
            style={{padding: "0 0 16px 0", gap: 1}}
          >
            <img alt="note_writing" src="/note_writing.svg" width={96}/>
          </Placeholder>
        </div>
        {
          isStateReady
          && (
            <article>
              <ActivitiesDateSelect activitiesData={activitiesState} onToggleHour={handleToggleHour}/>
              <section>
                <Subheadline level="1" weight="3">Select type</Subheadline>
                <ActivityTypesButtons onBtnClick={handleActivitySelect}/>
              </section>
            </article>
          )
        }
      </List>
    </Page>
  )
}

const activitiesReducer = (state: ActivitiesState, action: ActivityButtonAction) => {
  const { type } = action;
  switch (type) {
    case ActivityButtonActionType.TOGGLE: {
      const newState = [...state];
      newState[action.activityIndex!] = {
        ...newState[action.activityIndex!],
        isSelected: !newState[action.activityIndex!].isSelected,
      };
      return newState;
    }
    case ActivityButtonActionType.CHANGE_ACTIVITY: {
      const newHoursData = state
        .map((item) => item.isSelected ? {...item, activity: action.newActivityType!, isSelected: false} : item);

      if (newHoursData.every((item) => item.activity !== undefined)) {
        postEvent(
          'web_app_setup_main_button',
          {is_visible: true, is_active: true, text: 'Save data!'}
        );
      }
      return newHoursData;
    }
    case ActivityButtonActionType.FILL_ACTIVITIES: {
      return [...action.newActivities!];
    }
    default: {
      throw Error('Unknown action: ' + type);
    }
  }
}
