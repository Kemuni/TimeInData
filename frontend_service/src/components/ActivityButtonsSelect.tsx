import {FC, useMemo} from "react";
import {useState} from "react";
import {Button, Pagination, Subheadline} from "@telegram-apps/telegram-ui";
import {Icon20QuestionMark} from "@telegram-apps/telegram-ui/dist/icons/20/question_mark";
import {ActivityButtonStates, activityToIcon} from "@/types";


interface ActivityButtonsSelectProps {
  activitiesStates: ActivityButtonStates,
  onToggleButton: (index: number) => void,
  isToggledButton: (index: number) => boolean,
}

const MAX_ITEM_PER_PAGE = 9;
export const ActivityButtonsSelect: FC<ActivityButtonsSelectProps> = (
  { activitiesStates, onToggleButton, isToggledButton }
) => {
  const [currentPage, setCurrentPage] = useState(1);

  // Separate activities due to their date and amount on page
  const activitiesPages: ActivityButtonStates[] = useMemo(() => {
    let pageCounter: number = 0;
    const pages: ActivityButtonStates[] = [[activitiesStates[0]]];
    for (let i = 1; i < activitiesStates.length; ++i) {
      if (
        activitiesStates[i-1].local_date.getTime() !== activitiesStates[i].local_date.getTime()
        || pages[pageCounter].length === MAX_ITEM_PER_PAGE
      ) {
        pageCounter += 1;
        pages[pageCounter] = [activitiesStates[i]];
      } else {
        pages[pageCounter].push(activitiesStates[i]);
      }
    }
    return pages;
  }, [activitiesStates]);

  // For calculating index to toggle we store `activitiesDate` index of the first element which user see on the page.
  const startItemIndex = activitiesPages
    .slice(0, currentPage-1)
    .reduce((total, item) => total + item.length, 0);

  return (
    <section>
      <span className="flex gap-1.5 pb-2">
        <Subheadline level="1" weight="3">Select hours</Subheadline>
        <Subheadline level="2" weight="3" className="text-(--tgui--hint_color)">
          {
            activitiesPages[currentPage-1][0]
              .local_date
              .toLocaleString("en-US", { month: "long", day : 'numeric' })
          }
        </Subheadline>
      </span>
      <div>
        <div
          style={{
            display: 'grid',
            gap: 5,
            gridTemplateColumns: "repeat(3, 1fr)"
          }}
        >
          {
            activitiesPages[currentPage-1].map((item, index) => {
              const IconComponent = item.activity ? activityToIcon[item.activity] : undefined;
              const itemIndex = startItemIndex + index;
              return (
                <Button
                  key={item.local_hour}
                  size="m"
                  mode={(isToggledButton(itemIndex) ? "bezeled" : "gray")}
                  before={IconComponent ? <IconComponent /> : <Icon20QuestionMark/> }
                  onClick={() => onToggleButton(itemIndex)}
                >
                  {item.local_hour}:00
                </Button>
              );
            })
          }
        </div>

        {
          activitiesPages.length !== 1
          && <Pagination
                onChange={(_, page) => setCurrentPage(page)}
                count={activitiesPages.length}
                style={{justifyContent: 'center', padding: "16px 0 0 0"}}
            />
        }
      </div>
    </section>
  );
}
