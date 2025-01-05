import type {FC} from "react";
import {useState} from "react";
import {Button, Pagination} from "@telegram-apps/telegram-ui";
import {Icon20QuestionMark} from "@telegram-apps/telegram-ui/dist/icons/20/question_mark";
import ActivityBtnState from "@/types/ActivityBtnState.ts";
import {activityToIcon} from "@/types/ActivityType.ts";


interface HoursSelectProps {
  hoursData: ActivityBtnState[],
  onToggleHour: CallableFunction,
}

export const HourActivitiesSelect: FC<HoursSelectProps> = ({ hoursData, onToggleHour }) => {
  const [page, setPage] = useState(1);

  return (
    <div>
      <div
        style={{
          display: 'grid',
          gap: 5,
          gridTemplateColumns: "repeat(3, 1fr)"
        }}
      >
        {hoursData.slice((page - 1) * 9, page * 9).map((item) => {
          const IconComponent = item.activity ? activityToIcon[item.activity] : undefined;
          return (<Button
            key={item.hour}
            size="m"
            mode={(item.isSelected ? "bezeled" : "gray")}
            before={IconComponent ? <IconComponent /> : <Icon20QuestionMark/> }
            onClick={() => onToggleHour(item)}
          >
            {item.hour}:00
          </Button>);
        })}
      </div>

      {hoursData.length > 9 &&
          <Pagination
              onChange={(_, page) => setPage(page)}
              count={Math.floor(hoursData.length / 9) + 1}
              style={{justifyContent: 'center', padding: "16px 0 0 0"}}
          />
      }
    </div>
  );
}
