import {ActivityButtonsSelect} from "@/components/ActivityButtonsSelect.tsx";
import {Button, Modal, Placeholder, Spinner, Subheadline} from "@telegram-apps/telegram-ui";
import {ActivityTypesButtons} from "@/components/ActivityTypesButtons.tsx";
import {UseActivityButtonsReturn} from "@/hooks/useActivityButtons.ts";
import {FC, useEffect, useMemo, useState} from "react";
import {mainButton} from "@tma.js/sdk-react";
import {useMainButton} from "@/hooks";
import {ActivityButtonStates} from "@/types";
import {Icon24Checkmark} from "@/components/icons/Icon24Checkmark.tsx";

export interface HoursActivityFormProps extends UseActivityButtonsReturn {
  createActivities: (activities: ActivityButtonStates) => void,
  isActivitiesCreating: boolean,
  createActivitiesError: string,
}

export const HoursActivityForm: FC<HoursActivityFormProps> = ({
    activityButtonStates,
    toggleActivityBtn,
    changeActivityOfToggledBtns,
    isActivityBtnToggled,
    createActivities,
    isActivitiesCreating,
    createActivitiesError,
}) => {
  if (activityButtonStates.length === 0) throw new Error("Activity button states is empty");
  useEffect(() => {
    if (!mainButton.isMounted) {
      mainButton.mount();
      mainButton.hide();
    }
  }, []);

  const isReadyToSave = useMemo<boolean>(() => {
    return activityButtonStates.every((item) => item.activity !== undefined);
  }, [activityButtonStates]);

  const [modalWindowIsVisible, setModalWindowIsVisible] = useState<boolean>(false);

  useMainButton({
    text: "Save data!",
    isVisible: isReadyToSave,
    onClick: () => {
      createActivities(activityButtonStates);
      setModalWindowIsVisible(true);
      mainButton.hide();
    },
  });

  return (
    <>
      <Modal open={modalWindowIsVisible} title={"Status"}>
        <Placeholder
          header={isActivitiesCreating ? "Sending data..." : (createActivitiesError ?  "Error" : "Data is successfully sent!")}
          description={isActivitiesCreating ? "Wait please" : (createActivitiesError === '' ? "You can close it" : "Try again later!")}
        >
          {
            isActivitiesCreating
              ? <Spinner size="l" />
              : (!createActivitiesError && <Icon24Checkmark width={96} height={96}/>)
          }
        </Placeholder>
        {
          !isActivitiesCreating
          && <Button
                style={{display: "flex", margin: "auto", marginBottom: "25px"}}
                onClick={() => {
                  setModalWindowIsVisible(false);
                  window.location.reload();
                }}
                size="s"
            >
                Close Modal
            </Button>
        }
      </Modal>
      <article
        className="[&>section]:bg-(--tgui--bg_color) [&>section]:px-2 [&>section]:py-3 [&>section]:mb-2 [&>section]:rounded-lg"
      >
        <ActivityButtonsSelect
          activitiesStates={activityButtonStates}
          isToggledButton={isActivityBtnToggled}
          onToggleButton={toggleActivityBtn}
        />
        <section>
          <Subheadline level="1" weight="3" className="pb-2">Select type</Subheadline>
          <ActivityTypesButtons onBtnClick={changeActivityOfToggledBtns}/>
        </section>
      </article>
    </>
  );
}