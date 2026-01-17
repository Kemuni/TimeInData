import {usersApi} from "@/services";
import {useApiQuery} from "@/hooks";
import {useRawInitData} from "@tma.js/sdk-react";


export interface DateRange {
  fromDate: Date;
  toDate: Date;
}

export interface MissingActivitySlot {
  utcDate: Date;
  utcHour: number;
}

export interface MissingActivitySlots {
  hasMissingSlots: boolean;
  dateRange?: DateRange
  missingSlots?: MissingActivitySlot[]
  totalMissing: number;
}

export function useGetClosestMissingActivitySlots() {
  const rawInitData = useRawInitData();
  return useApiQuery<MissingActivitySlots | null>({
    queryFn: async () => {
      if (!rawInitData) throw new Error('rawInitData is required for authentication');
      const response = await usersApi.getClosestMissingActivitySlots(rawInitData);

      if (!response.success || !response.data) return null;
      const data = response.data;

      const dateRange: DateRange | undefined = data.date_range ? {
        fromDate: new Date(data.date_range.from_date),
        toDate: new Date(data.date_range.to_date),
      } : undefined;

      const missingSlots: Array<MissingActivitySlot> | undefined = data.missing_slots !== undefined && data.missing_slots?.length > 0
        ? data.missing_slots.map(slot => ({
            utcDate: new Date(`${slot.utc_date}T00:00:00`),
            utcHour: Number(slot.utc_hour),
          }))
        : undefined;

      return {
        hasMissingSlots: data.has_missing_slots,
        dateRange: dateRange,
        missingSlots: missingSlots,
        totalMissing: Number(data.total_missing),
      };
    },
    enabled: !!rawInitData,
  });
}
