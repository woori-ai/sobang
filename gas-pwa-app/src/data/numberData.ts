export interface NumberGasItem {
  id: string;
  name: string;
  question: string;
  targetValue: string;
  displayShort: string;
  lowerBound?: string;
  upperBound?: string;
  unit: string;
  fullDisplay: string;
  color: string;
}

export const KEY_NUMBERS_DATA: NumberGasItem[] = [
  {
    id: 'propane',
    name: '프로판',
    question: '프로판(C₃H₈)의 폭발 범위는?',
    targetValue: '2.1 ~ 9.5%',
    displayShort: '2.1 ~ 9.5%',
    lowerBound: '2.1',
    upperBound: '9.5',
    unit: '%',
    fullDisplay: '2.1 ~ 9.5%',
    color: '#3B82F6', // Blue
  },
  {
    id: 'butane',
    name: '부탄',
    question: '부탄(C₄H₁₀)의 폭발 범위는?',
    targetValue: '1.8 ~ 8.4%',
    displayShort: '1.8 ~ 8.4%',
    lowerBound: '1.8',
    upperBound: '8.4',
    unit: '%',
    fullDisplay: '1.8 ~ 8.4%',
    color: '#10B981', // Emerald
  },
  {
    id: 'acetylene',
    name: '아세틸렌',
    question: '아세틸렌(C₂H₂)의 폭발 범위는?',
    targetValue: '2.5 ~ 81%',
    displayShort: '2.5 ~ 81%',
    lowerBound: '2.5',
    upperBound: '81',
    unit: '%',
    fullDisplay: '2.5 ~ 81%',
    color: '#EAB308', // Yellow
  },
  {
    id: 'hydrogen',
    name: '수소',
    question: '수소(H₂)의 폭발 범위는?',
    targetValue: '4 ~ 75%',
    displayShort: '4 ~ 75%',
    lowerBound: '4',
    upperBound: '75',
    unit: '%',
    fullDisplay: '4 ~ 75%',
    color: '#F97316', // Orange
  },
  {
    id: 'toxic',
    name: '독성가스',
    question: '독성가스의 LC₅₀ 기준 수치는?',
    targetValue: 'LC50 ≤ 5,000 ppm',
    displayShort: 'LC₅₀ ≤ 5000 ppm',
    lowerBound: '5000',
    unit: 'ppm',
    fullDisplay: 'LC₅₀ ≤ 5,000 ppm',
    color: '#EC4899', // Pink
  },
  {
    id: 'flammable',
    name: '가연성가스',
    question: '가연성가스의 폭발하한 및 상하한차 기준은?',
    targetValue: '하한 10% 이하 / 차 20% 이상',
    displayShort: '하한 10% / 차 20%',
    lowerBound: '10',
    upperBound: '20',
    unit: '%',
    fullDisplay: '하한 10% 이하 OR 차 20% 이상',
    color: '#8B5CF6', // Purple
  },
];
