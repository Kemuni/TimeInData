import {FC} from "react";

import {Icon24Book} from "@/components/icons/Icon24Book.tsx";
import {Icon24Heart} from "@/components/icons/Icon24Heart.tsx";
import {Icon24Group} from "@/components/icons/Icon24Group.tsx";
import {Icon24TeaCup} from "@/components/icons/Icon24TeaCup.tsx";
import {Icon24Dumbbell} from "@/components/icons/Icon24Dumbbell.tsx";
import {Icon24Gamepad} from "@/components/icons/Icon24Gamepad.tsx";
import {Icon24Suitcase} from "@/components/icons/Icon24Suitcase.tsx";
import {Icon24NightMode} from "@/components/icons/Icon24NightMode.tsx";


export enum ActivityType {
  Sleep = "SLEEP",
  Work = "WORK",
  Study = "STUDY",
  Family = "FAMILY",
  Friends = "FRIENDS",
  Passive = "PASSIVE",
  Sport = "SPORT",
  Games = "GAMES",
}


export enum ActivityIntType {
  Sleep,
  Work,
  Study,
  Family,
  Friends,
  Passive,
  Sport,
  Games,
}


export const activityToIcon: { [key in ActivityType]: FC } = {
  [ActivityType.Sleep]: Icon24NightMode,
  [ActivityType.Work]: Icon24Suitcase,
  [ActivityType.Study]: Icon24Book,
  [ActivityType.Family]: Icon24Heart,
  [ActivityType.Friends]: Icon24Group,
  [ActivityType.Passive]: Icon24TeaCup,
  [ActivityType.Sport]: Icon24Dumbbell,
  [ActivityType.Games]: Icon24Gamepad,
};

