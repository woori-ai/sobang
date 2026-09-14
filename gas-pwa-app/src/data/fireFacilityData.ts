import type { FireFacilityCategory, FireEquipmentItem } from '../types/fireFacility';

// 1. 소방시설의 5대 분류 (고정 리스트)
export const FIRE_FACILITY_CATEGORIES: FireFacilityCategory[] = [
  {
    id: 'extinguishing',
    name: '소화설비',
    color: '#3B82F6', // Blue
    bgHex: 'rgba(59, 130, 246, 0.15)',
    borderHex: '#3B82F6',
    badgeColor: '#60A5FA',
    icon: '🔥',
    description: '물 또는 소화약제를 사용하여 화재를 진화하는 설비',
    totalCount: 5,
  },
  {
    id: 'alarm',
    name: '경보설비',
    color: '#EAB308', // Amber
    bgHex: 'rgba(234, 179, 8, 0.15)',
    borderHex: '#EAB308',
    badgeColor: '#FBBF24',
    icon: '🔔',
    description: '화재 발생 사실을 소리, 빛 등으로 관계인에게 전파하는 설비',
    totalCount: 5,
  },
  {
    id: 'evacuation',
    name: '피난구조설비',
    color: '#10B981', // Emerald
    bgHex: 'rgba(16, 185, 129, 0.15)',
    borderHex: '#10B981',
    badgeColor: '#34D399',
    icon: '🏃',
    description: '화재 시 피난하거나 인명을 구조하기 위해 사용하는 기구 및 설비',
    totalCount: 4,
  },
  {
    id: 'water-supply',
    name: '소화용수설비',
    color: '#06B6D4', // Cyan
    bgHex: 'rgba(6, 182, 212, 0.15)',
    borderHex: '#06B6D4',
    badgeColor: '#22D3EE',
    icon: '💧',
    description: '화재 진압에 필요한 소화용수를 확보·공급하는 설비',
    totalCount: 2,
  },
  {
    id: 'fire-fighting',
    name: '소화활동설비',
    color: '#EC4899', // Pink
    bgHex: 'rgba(236, 72, 153, 0.15)',
    borderHex: '#EC4899',
    badgeColor: '#F472B6',
    icon: '🚒',
    description: '화재 진압 활동이나 인명 구조 활동을 수행하는 소방관이 사용하는 설비',
    totalCount: 6,
  },
];

// 2. 주요 구성 설비 전체 22종 리스트
export const FIRE_EQUIPMENT_ITEMS: FireEquipmentItem[] = [
  // 1) 소화설비 (5종)
  {
    id: 'exting-1',
    name: '소화기구',
    categoryId: 'extinguishing',
    categoryName: '소화설비',
    detail: '소화기, 자동소화장치, 수동식소화기 등',
  },
  {
    id: 'exting-2',
    name: '옥내소방전설비',
    categoryId: 'extinguishing',
    categoryName: '소화설비',
    detail: '건물 내부 초기 화재 진압용 수계 소화설비',
  },
  {
    id: 'exting-3',
    name: '옥외소방전설비',
    categoryId: 'extinguishing',
    categoryName: '소화설비',
    detail: '건물 외부 1·2층 화재 진압 및 인접 건물 연소 방지용',
  },
  {
    id: 'exting-4',
    name: '스프링클러설비',
    categoryId: 'extinguishing',
    categoryName: '소화설비',
    detail: '화재 감지 시 헤드에서 자동으로 방수되는 소화설비 (습식/건식/준비작동식)',
  },
  {
    id: 'exting-5',
    name: '물분무등소화설비',
    categoryId: 'extinguishing',
    categoryName: '소화설비',
    detail: '가스계소화설비(CO2, 할론, 분말), 포소화, 미분무소화설비 등',
  },

  // 2) 경보설비 (5종)
  {
    id: 'alarm-1',
    name: '단독경보형감지기',
    categoryId: 'alarm',
    categoryName: '경보설비',
    detail: '건전지 내장형으로 자체 음향으로 화재를 알리는 감지기',
  },
  {
    id: 'alarm-2',
    name: '비상경보설비',
    categoryId: 'alarm',
    categoryName: '경보설비',
    detail: '비상벨설비 및 자동식 사이렌 설비',
  },
  {
    id: 'alarm-3',
    name: '자동화재탐지설비',
    categoryId: 'alarm',
    categoryName: '경보설비',
    detail: '감지기, 수신기, 발신기, 음향장치로 구성된 대표적 경보설비',
  },
  {
    id: 'alarm-4',
    name: '비상방송설비',
    categoryId: 'alarm',
    categoryName: '경보설비',
    detail: '화재 발생 시 앰프 및 확성기를 통한 육성/자동 비상방송',
  },
  {
    id: 'alarm-5',
    name: '자동화재속보설비',
    categoryId: 'alarm',
    categoryName: '경보설비',
    detail: '화재 신호를 감지하여 소방관서(119)로 자동 통보하는 설비',
  },

  // 3) 피난구조설비 (4종)
  {
    id: 'evac-1',
    name: '피난기구',
    categoryId: 'evacuation',
    categoryName: '피난구조설비',
    detail: '완강기, 구조대, 피난하강기, 다수인피난장비 등',
  },
  {
    id: 'evac-2',
    name: '인명구조기구',
    categoryId: 'evacuation',
    categoryName: '피난구조설비',
    detail: '방열복·방화복, 공기호흡기, 인공소생기',
  },
  {
    id: 'evac-3',
    name: '유도등 / 유도표지',
    categoryId: 'evacuation',
    categoryName: '피난구조설비',
    detail: '피난구유도등, 통로유도등, 객석유도등 및 유도표지',
  },
  {
    id: 'evac-4',
    name: '비상조명등',
    categoryId: 'evacuation',
    categoryName: '피난구조설비',
    detail: '정전 시 작동하는 예비전원 내장 비상 조명 장치',
  },

  // 4) 소화용수설비 (2종)
  {
    id: 'water-1',
    name: '상수도소화용수설비',
    categoryId: 'water-supply',
    categoryName: '소화용수설비',
    detail: '상수도 배관과 연결된 소화전 (호수구경 75mm 이상)',
  },
  {
    id: 'water-2',
    name: '소화수조 및 저수조',
    categoryId: 'water-supply',
    categoryName: '소화용수설비',
    detail: '소방차 연결 수조 및 채수구 장치',
  },

  // 5) 소화활동설비 (6종)
  {
    id: 'activity-1',
    name: '제연설비',
    categoryId: 'fire-fighting',
    categoryName: '소화활동설비',
    detail: '거실제연 및 특별피난계단 부속실 제연 (차압 유지를 통한 연기 차단)',
  },
  {
    id: 'activity-2',
    name: '연결송수관설비',
    categoryId: 'fire-fighting',
    categoryName: '소화활동설비',
    detail: '소방차가 송수구에 가압 송수하여 고층부 방수구로 공급',
  },
  {
    id: 'activity-3',
    name: '연결살수설비',
    categoryId: 'fire-fighting',
    categoryName: '소화활동설비',
    detail: '지하가·지하층 화재 시 소방차에서 살수헤드로 송수',
  },
  {
    id: 'activity-4',
    name: '비상콘센트설비',
    categoryId: 'fire-fighting',
    categoryName: '소화활동설비',
    detail: '소방관 전원용 콘센트 (단상 220V / 3상 380V)',
  },
  {
    id: 'activity-5',
    name: '무선통신보조설비',
    categoryId: 'fire-fighting',
    categoryName: '소화활동설비',
    detail: '지하층/고층 터널 내 무선통신용 누설동축케이블 및 안테나',
  },
  {
    id: 'activity-6',
    name: '연기제거설비',
    categoryId: 'fire-fighting',
    categoryName: '소화활동설비',
    detail: '지하층 및 무창층 연기 강제 배출 장치',
  },
];

// Helper: 셔플 함수
export function getShuffledEquipmentItems(): FireEquipmentItem[] {
  return [...FIRE_EQUIPMENT_ITEMS].sort(() => Math.random() - 0.5);
}
