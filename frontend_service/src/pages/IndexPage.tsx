import {FC, useCallback} from "react";
import {initData, useSignal} from "@tma.js/sdk-react";
import {List, Placeholder, Spinner} from "@telegram-apps/telegram-ui";
import {Page} from "@/components/Page.tsx";
import {useActivityButtons} from "@/hooks/useActivityButtons.ts";
import {HoursActivityForm} from "@/components/forms/HoursActivityForm.tsx";
import {useCreateActivities, useGetClosestMissingActivitySlots} from "@/hooks";
import {ActivityButtonStates} from "@/types";

export const IndexPage: FC = () => {
  const initDataState = useSignal(initData.state);
  const userId = initDataState?.user?.id;

  const {
    data: missingActivitySlots,
    isLoading,
    error
  } = useGetClosestMissingActivitySlots();

  const {
    mutate: createActivities,
    isLoading: isActivitiesCreating,
    error: createActivitiesError
  } = useCreateActivities();

  const createActivitiesByForm = useCallback(
    async (activityButtonStates: ActivityButtonStates) => {
      if (!activityButtonStates.every((btnState) => btnState.activity !== undefined))
        throw new Error("All activity buttons must be toggled");

      await createActivities({
        activities: activityButtonStates
          .map((btnState) => ({
            type: btnState.activity!,
            utc_date: btnState.utc_date,
            utc_hour: btnState.utc_hour,
          })),
      });
    }, []);

  const {
    activityButtonStates,
    toggleActivityBtn,
    changeActivityOfToggledBtns,
    isActivityBtnToggled,
  } = useActivityButtons({
    utcMissingActivitySlots: missingActivitySlots?.missingSlots,
  });


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
        {
          userId
            ? (
              <Placeholder
                header={
                  missingActivitySlots !== null && (missingActivitySlots.totalMissing !== 0
                    ? "Set your activities!"
                    : "You have already set your activities!")
                }
                description={
                  missingActivitySlots !== null && missingActivitySlots.totalMissing === 0 && "You can close this page"
                }
                className="pb-4! gap-0.5!">
                <img alt="note_writing" src="/note_writing.svg" width={96} />
              </Placeholder>
            )
            : (
              <Placeholder header="Waiting for Telegram"
                           description="Please wait, we are waiting for Telegram to send us your user id">
                <Spinner size="l" />
              </Placeholder>
            )
        }
        {
          isLoading &&
            (
              <Placeholder header="Loading..." description="Please wait, we are loading your missing activity slots">
                <Spinner size="l" />
              </Placeholder>
            )
        }
        {
          !isLoading && !error && activityButtonStates.length > 0 &&
            (
              <HoursActivityForm
                activityButtonStates={activityButtonStates}
                changeActivityOfToggledBtns={changeActivityOfToggledBtns}
                toggleActivityBtn={toggleActivityBtn}
                isActivityBtnToggled={isActivityBtnToggled}
                createActivities={createActivitiesByForm}
                isActivitiesCreating={isActivitiesCreating}
                createActivitiesError={createActivitiesError}
              />
            )
        }
      </List>
    </Page>
  );
}
