export type FireFacilityCategoryId =
  | 'extinguishing'
  | 'alarm'
  | 'evacuation'
  | 'water-supply'
  | 'fire-fighting';

export interface FireFacilityCategory {
  id: FireFacilityCategoryId;
  name: string; // 소방시설 종류 (e.g., '소화설비')
  color: string;
  bgHex: string;
  borderHex: string;
  badgeColor: string;
  icon: string;
  description: string;
  totalCount: number;
}

export interface FireEquipmentItem {
  id: string;
  name: string; // 주요 구성 설비 (e.g., '스프링클러설비')
  categoryId: FireFacilityCategoryId;
  categoryName: string; // '소화설비'
  detail: string;
}

export type GameMode = 'full-match' | 'speed-quiz';
