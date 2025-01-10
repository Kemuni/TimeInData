import {FC} from "react";
import {useState} from "react";
import {Button, Pagination, Subheadline} from "@telegram-apps/telegram-ui";
import {Icon20QuestionMark} from "@telegram-apps/telegram-ui/dist/icons/20/question_mark";
import ActivityBtnState from "@/types/ActivityBtnState.ts";
import {activityToIcon} from "@/types/ActivityType.ts";


interface HoursSelectProps {
  activitiesData: ActivityBtnState[],
  onToggleHour: (index: number) => void,
}

const MAX_ITEM_PER_PAGE = 9;
export const ActivitiesDateSelect: FC<HoursSelectProps> = ({ activitiesData, onToggleHour }) => {
  const [page, setPage] = useState(1);

  // Separate activities due to their date and amount on page
  const activitiesPages: ActivityBtnState[][]  = [[activitiesData[0]]];

  let pageCounter: number = 0;
  for (let i = 1; i < activitiesData.length; ++i) {
    if (
      activitiesData[i-1].date.getDate() !== activitiesData[i].date.getDate()
      || activitiesPages[pageCounter].length === MAX_ITEM_PER_PAGE
    ) {
      pageCounter += 1;
      activitiesPages[pageCounter] = [activitiesData[i]];
    } else {
      activitiesPages[pageCounter].push(activitiesData[i]);
    }
  }

  // `activitiesDate` index of the first element which user see on the page
  const startItemIndex = activitiesPages
    .slice(0, page-1)
    .reduce((total, item) => total + item.length, 0);

  return (
    <section>
      <div
        style={{
          display: 'flex',
          gap: 6
        }}
      >
        <Subheadline level="1" weight="3">Select hours</Subheadline>
        <Subheadline level="2" weight="3" style={{color: "var(--tgui--hint_color)"}}>
          {activitiesPages[page-1][0].date.toLocaleString("en-US", { month: "long", day : 'numeric' })}
        </Subheadline>
      </div>
      <div>
        <div
          style={{
            display: 'grid',
            gap: 5,
            gridTemplateColumns: "repeat(3, 1fr)"
          }}
        >
          {
            activitiesPages[page-1].map((item, index) => {
              const IconComponent = item.activity ? activityToIcon[item.activity] : undefined;
              return (
                <Button
                  key={item.date.getHours()}
                  size="m"
                  mode={(item.isSelected ? "bezeled" : "gray")}
                  before={IconComponent ? <IconComponent /> : <Icon20QuestionMark/> }
                  onClick={() => onToggleHour(startItemIndex + index)}
                >
                  {item.date.getHours()}:00
                </Button>
              );
            })
          }
        </div>

        {
          activitiesPages.length !== 0
          && <Pagination
                onChange={(_, page) => setPage(page)}
                count={activitiesPages.length}
                style={{justifyContent: 'center', padding: "16px 0 0 0"}}
            />
        }
      </div>
    </section>
  );
}
