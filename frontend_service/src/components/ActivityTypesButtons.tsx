import {
  InlineButtonsItem
} from "@telegram-apps/telegram-ui/dist/components/Blocks/InlineButtons/components/InlineButtonsItem/InlineButtonsItem";
import {InlineButtons} from "@telegram-apps/telegram-ui";
import {activityToIcon, ActivityType} from "@/types/ActivityType.ts";
import {FC} from "react";

interface ActivityTypesButtonsProps {
  onBtnClick: (activity: ActivityType) => void,
}

export const ActivityTypesButtons: FC<ActivityTypesButtonsProps> = ({ onBtnClick }) => (
  <InlineButtons style={{flexFlow: "wrap"}}>
    {(Object.keys(ActivityType) as Array<keyof typeof ActivityType>).map((key) => {
      const activity = ActivityType[key];
      const IconComponent = activityToIcon[activity];
      return (<InlineButtonsItem mode="gray" key={key} text={key} onClick={() => onBtnClick(activity)}>
        <IconComponent />
      </InlineButtonsItem>);
    })}
  </InlineButtons>
);
