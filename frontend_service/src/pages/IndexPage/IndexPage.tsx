import {FC, useCallback, useEffect, useReducer, useState} from "react";
import {Button, List, Modal, Placeholder, Spinner, Subheadline,} from "@telegram-apps/telegram-ui";

import "./IndexPage.scss";
import {ActivitiesDateSelect} from "@/components/ActivitiesDateSelect.tsx";
import {ActivityTypesButtons} from "@/components/ActivityTypesButtons.tsx";
import {ActivityType} from "@/types/ActivityType.ts";
import {
  backButton,
  initDataState as _initDataState,
  mainButton,
  useSignal
} from "@telegram-apps/sdk-react";
import ActivityBtnState from "@/types/ActivityBtnState.ts";
import {Page} from "@/components/Page.tsx";
import {useCreateNewActivities, useGetLastUserActivity} from "@/hooks/activity.ts";
import {Icon24Checkmark} from "@/components/icons/Icon24Checkmark.tsx";
import ActivityState from "@/types/ActivityState.ts";

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
 * Get activities that user have to fill, based on last filled activity. Maximum is 12 hours items.
 * 6 hours items for newbie.
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
    // If user is newbie for us, we show him only last seven hours for activities filling
    lastActivityDate = new Date(currentDate.getTime() - 7 * OneHourInMs);
  }


  // Now get hours activities to fill, but less than 12 items
  const diffMs: number = (currentDate.getTime() - lastActivityDate.getTime());
  let diffHours: number = Math.floor(diffMs / OneHourInMs) - 1;
  if (diffHours > 12) diffHours = 12;

  const activitiesStateToSet: ActivitiesState = [];
  for (let i: number = diffHours; i != 0; i--) {
    const msOffsetToActivityHour: number = i * OneHourInMs;
    activitiesStateToSet.push({date: new Date(currentDate.getTime() - msOffsetToActivityHour)})
  }
  return activitiesStateToSet;
}


/**
 * Get header and description of Placeholder component based on Activities States data.
 * @param isLoading - Is data about Activities state is loading.
 * @param hasError - True if we have some errors after loading data about Activities, otherwise - false.
 * @param isActivitiesStateEmpty - True if we don't have any activities to set by user, otherwise - false.
 * @return Arguments for Placeholder component about loading Activities States data.
 */
function getPlaceholderTexts(
  isLoading: boolean, hasError: boolean, isActivitiesStateEmpty: boolean
): {header: string, description: string} {
  if (isLoading) return {
      header: 'Loading data...',
      description: 'Wait a little',
    }
  else if (hasError) return {
      header: "Some error occurs :(",
      description: "Try again later!",
    }
  else if (isActivitiesStateEmpty) return {
      header: "All activities are set!",
      description: "You set all your activities, great job, buddy",
    }
  else return {
    header: "Set your activities",
    description: "",
  }
}


export const IndexPage: FC = () => {
  const initDataState = useSignal(_initDataState);

  const { lastActivity, isLoading, error} = useGetLastUserActivity(initDataState?.user?.id);

  const { createNewActivities, isLoading: isCreationLoading, error: creationError } =
    useCreateNewActivities(initDataState?.user?.id);
  const initActivities: ActivitiesState = [];
  const [activitiesState, dispatchActivities] = useReducer(activitiesReducer, initActivities);

  // State below means that the modal status window for creation new activities is visible
  const [ modalWindowIsVisible, setModalWindowIsVisible ] = useState(false);

  // Main button as "save" button
  const saveNewActivities = useCallback(async () => {
    if (activitiesState.some((item) => item.activity === undefined))
      return;

    setModalWindowIsVisible(true);
    await createNewActivities(activitiesState as ActivityState[]);

    // Clear activities to show the final placeholder of activities saving
    dispatchActivities({
      type: ActivityButtonActionType.FILL_ACTIVITIES,
      newActivities: [],
    });
  }, [activitiesState]);

  // Main button function handler
  useEffect(() => {
    mainButton.mount();
    mainButton.setParams({
      isVisible: false,
      isEnabled: false,
      text: '',
    });

    async function handleMainButton() {
      mainButton.setParams({
        isVisible: false,
        isEnabled: false,
        text: 'Close',
      });
      await saveNewActivities();
    }

    mainButton.onClick(handleMainButton);

    return () => { backButton.mount(); mainButton.offClick(handleMainButton); };
  }, []);

  // Fill initial activities
  useEffect(() => {
    if (isLoading || error !== '') return;
    dispatchActivities({
      type: ActivityButtonActionType.FILL_ACTIVITIES,
      newActivities: [...getActivitiesToFill(lastActivity?.time)],
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

  const isReadyToFillActivities = (!isLoading && error === '' && activitiesState.length !== 0);

  return (
    <Page back={false}>
      <Modal open={modalWindowIsVisible} title={"Status"}>
        <Placeholder
          header={isCreationLoading ? "Sending data..." : (creationError ?  "Error" : "Data is successfully sent!")}
          description={isCreationLoading ? "Wait please" : (creationError === '' ? "You can close it" : "Try again later!")}
        >
          {
            isCreationLoading
              ? <Spinner size="l" />
              : <Icon24Checkmark width={96} height={96}/>
          }
        </Placeholder>
        {
          !isCreationLoading
          && <Button
                style={{display: "flex", margin: "auto", marginBottom: "25px"}}
                onClick={() => setModalWindowIsVisible(false)}
                size="s"
            >
                Close Modal
            </Button>
        }
      </Modal>

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
            {...getPlaceholderTexts(isLoading, error !== '', activitiesState.length === 0)}
            style={{padding: "0 0 16px 0", gap: 1}}
          >
            {
              isLoading
                ? <Spinner size="l" />
                : <img alt="note_writing" src="/note_writing.svg" width={96} />
            }
          </Placeholder>
        </div>
        {
          isReadyToFillActivities
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
        mainButton.setParams({
          isVisible: true,
          isEnabled: true,
          text: 'Save data!',
        });
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
