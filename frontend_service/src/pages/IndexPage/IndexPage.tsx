import {FC, useEffect} from "react";
import {useReducer} from "react";
import {List, Placeholder, Subheadline,} from "@telegram-apps/telegram-ui";

import "./IndexPage.scss";
import {HourActivitiesSelect} from "@/components/HourActivitiesSelect.tsx";
import {ActivityTypesButtons} from "@/components/ActivityTypesButtons.tsx";
import {ActivityType} from "@/types/ActivityType.ts";
import {postEvent} from "@telegram-apps/sdk-react";
import ActivityBtnState from "@/types/ActivityBtnState.ts";
import {Page} from "@/components/Page.tsx";

enum ActivityButtonActionType {
  TOGGLE = "TOGGLE",
  CHANGE_ACTIVITY = "CHANGE_ACTIVITY"
}

type ActivitiesState = ActivityBtnState[];

interface  ActivityButtonAction {
  type: ActivityButtonActionType
  hour?: number
  newActivity?: ActivityType
}

export const IndexPage: FC = () => {
  useEffect(() => {
    postEvent(
    'web_app_setup_main_button',
    {
      is_visible: false,
      is_active: false,
      text: 'Save activities',
    });
  }, []);
  const initActivities: ActivitiesState = [
    {hour: 7}, {hour: 8}, {hour: 9}, {hour: 10}, {hour: 11}, {hour: 12}, {hour: 13}, {hour: 14}, {hour: 15},
    {hour: 16}
  ];
  const [activitiesState, dispatchActivities] = useReducer(activitiesReducer, initActivities);

  function handleToggleHour(item: ActivityBtnState)  {
    dispatchActivities({
      type: ActivityButtonActionType.TOGGLE,
      hour: item.hour,
    });
  }

  function handleActivitySelect(activity: ActivityType) {
    dispatchActivities({
      type: ActivityButtonActionType.CHANGE_ACTIVITY,
      newActivity: activity,
    });
  }

  return (
    <Page back={false}>
      <List style={{backgroundColor: "var(--tgui--secondary_bg_color)", height: "100vh"}}>
        <div style={{maxWidth: "250px", margin: "auto"}}>
          <Placeholder header="Set activities" style={{padding: "0 0 16px 0", gap: 1}}>
            <img src="/note_writing.svg" width={96}/>
          </Placeholder>
        </div>
        <article>
          <section>
            <div
              style={{
                display: 'flex',
                gap: 6
              }}>
              <Subheadline level="1" weight="3">Select hours</Subheadline>
              <Subheadline level="2" weight="3" style={{color: "var(--tgui--hint_color)"}}>
                {new Date().toLocaleString("en-US", { month: "long", day : 'numeric' })}
              </Subheadline>
            </div>
            <HourActivitiesSelect hoursData={activitiesState} onToggleHour={handleToggleHour}/>
          </section>
          <section>
            <Subheadline level="1" weight="3">Select type</Subheadline>
            <ActivityTypesButtons onBtnClick={handleActivitySelect} />
          </section>
        </article>
      </List>
    </Page>
  )
}

const activitiesReducer = (state: ActivitiesState, action: ActivityButtonAction) => {
  const { type, hour, newActivity } = action;
  switch (type) {
    case ActivityButtonActionType.TOGGLE: {
      return state
        .map((item) => item.hour === hour ? {...item, isSelected: !item.isSelected} : item);
    }
    case ActivityButtonActionType.CHANGE_ACTIVITY: {
      const newHoursData = state
        .map((item) => item.isSelected ? {...item, activity: newActivity, isSelected: false} : item);

      if (newHoursData.every((item) => item.activity !== undefined)) {
        postEvent(
          'web_app_setup_main_button',
          {is_visible: true, is_active: true, text: 'Save data!'}
        );
      }
      return newHoursData;
    }
    default: {
      throw Error('Unknown action: ' + type);
    }
  }
}
