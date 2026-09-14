import type { GasItem } from '../types/game';

// 전체 10종 가스 데이터베이스
export const ALL_GAS_DATA: GasItem[] = [
  {
    id: 'oxygen',
    korean: '산소',
    formula: 'O₂',
    colorName: '백색',
    colorHex: '#FFFFFF',
    borderHex: '#E0E0E0',
    isDarkText: true,
  },
  {
    id: 'acetylene',
    korean: '아세틸렌',
    formula: 'C₂H₂',
    colorName: '황색',
    colorHex: '#FDD835',
    borderHex: '#F57F17',
    isDarkText: true,
  },
  {
    id: 'hydrogen',
    korean: '수소',
    formula: 'H₂',
    colorName: '주황색',
    colorHex: '#FF7043',
    borderHex: '#E64A19',
  },
  {
    id: 'ammonia',
    korean: '암모니아',
    formula: 'NH₃',
    colorName: '백색',
    colorHex: '#FFFFFF',
    borderHex: '#E0E0E0',
    isDarkText: true,
  },
  {
    id: 'sulfurDioxide',
    korean: '아황산가스',
    formula: 'SO₂',
    colorName: '검정색',
    colorHex: '#212121',
    borderHex: '#424242',
  },
  {
    id: 'co2',
    korean: '탄산가스',
    formula: 'CO₂',
    colorName: '청색',
    colorHex: '#1E88E5',
    borderHex: '#1565C0',
  },
  {
    id: 'lpg',
    korean: 'LPG',
    formula: 'C₃H₈',
    colorName: '회색',
    colorHex: '#9E9E9E',
    borderHex: '#616161',
  },
  {
    id: 'chlorine',
    korean: '염소',
    formula: 'Cl₂',
    colorName: '갈색',
    colorHex: '#8D6E63',
    borderHex: '#5D4037',
  },
  {
    id: 'nitrogen',
    korean: '질소',
    formula: 'N₂',
    colorName: '회색',
    colorHex: '#9E9E9E',
    borderHex: '#616161',
  },
  {
    id: 'lng',
    korean: 'LNG',
    formula: 'CH₄',
    colorName: '회색',
    colorHex: '#9E9E9E',
    borderHex: '#616161',
  },
];

// 필수 고정 7종 가스 목록 (유저 지정)
export const FIXED_BASE_GAS_IDS = [
  'oxygen',        // 산소-백색
  'acetylene',     // 아세틸렌-황색
  'hydrogen',      // 수소-주황색
  'ammonia',       // 암모니아-백색
  'sulfurDioxide', // 아황산가스-검정색
  'co2',           // 탄산가스-청색
  'lpg',           // LPG-회색
];

// 게임 라운드별 가스 생성 (기본 7종 + 나머지 3종 무작위 조합)
export function generateGameRoundGases(): GasItem[] {
  const fixedGases = ALL_GAS_DATA.filter((g) => FIXED_BASE_GAS_IDS.includes(g.id));
  const remainingGases = ALL_GAS_DATA.filter((g) => !FIXED_BASE_GAS_IDS.includes(g.id));

  // 나머지 가스 랜덤 셔플
  const shuffledRemaining = [...remainingGases].sort(() => Math.random() - 0.5);

  // 기본 7종 + 무작위 가스 포함 (전체 10종)
  const fullList = [...fixedGases, ...shuffledRemaining];

  // 전체 무작위 순서 셔플
  return fullList.sort(() => Math.random() - 0.5);
}
