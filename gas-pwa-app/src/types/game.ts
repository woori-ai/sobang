export type GasItem = {
  id: string;
  korean: string;     // 한글 이름
  formula: string;    // 원소기호
  colorName: string;  // 용기 색상 이름
  colorHex: string;   // 실제 색상 코드
  borderHex: string;  // 경계선 테두리 색상
  isDarkText?: boolean;
};

export type Stage = 1 | 2 | 3; // 1: 이름 선택, 2: 원소기호 선택, 3: 색상 선택

export type BubbleData = {
  id: string;          // gasId
  gasId: string;
  label: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  colorHex?: string;
  borderHex?: string;
  isDarkText?: boolean;
};

export type ActiveGasTarget = {
  id: string;
  korean: string;
  formula: string;
};

export type MatchedSet = {
  gasId: string;
  korean: string;
  formula: string;
  colorName: string;
  colorHex: string;
};

export type ScorePopup = {
  id: number;
  amount: number;
  x: number;
  y: number;
};
