/**
 * 소방안전관리자 1급 마스터 - 메인 컨트롤러 (Vanilla JS)
 */

(function () {
  'use strict';

  // 1. 상태(State) 관리
  const state = {
    activeTab: 'mcq', // 'mcq' | 'box' | 'cards' | 'calc'
    data: {
      mcq: [],
      box: [],
      cards: [],
      calc: [],
      pic: []
    },
    filteredList: [],
    currentIndex: 0,
    filters: {
      chapter: 'all',
      difficulty: 'all',
      bookmarkOnly: false,
      incorrectOnly: false,
      unsolvedOnly: false,
      imageOnly: false,
      alwaysShowExplanation: false
    },
    userStore: {
      answers: {},    // { [tab]: { [itemId]: { selected: any, isCorrect: boolean } } }
      bookmarks: {},  // { [tab]: { [itemId]: boolean } }
      settings: {
        theme: 'dark',
        fontSize: 'medium'
      }
    }
  };

  const STORAGE_KEY = 'sobang_master_v1';

  // 2. DOM 요소 캐싱
  const dom = {
    // 헤더 & 진도
    themeBtn: document.getElementById('theme-toggle-btn'),
    settingsBtn: document.getElementById('settings-btn'),
    progressPercent: document.getElementById('progress-percent'),
    accuracyRate: document.getElementById('accuracy-rate'),
    answeredCount: document.getElementById('answered-count'),
    totalPoolCount: document.getElementById('total-pool-count'),
    progressBarFill: document.getElementById('progress-bar-fill'),

    // 탭 & 배지
    tabs: document.querySelectorAll('.nav-tab'),
    badgeMcq: document.getElementById('badge-mcq'),
    badgeBox: document.getElementById('badge-box'),
    badgeCards: document.getElementById('badge-cards'),
    badgeCalc: document.getElementById('badge-calc'),
    badgePic: document.getElementById('badge-pic'),

    // 필터
    chapterFilter: document.getElementById('chapter-filter'),
    diffFilter: document.getElementById('diff-filter'),
    filterBookmarkBtn: document.getElementById('filter-bookmark-btn'),
    filterIncorrectBtn: document.getElementById('filter-incorrect-btn'),
    filterUnsolvedBtn: document.getElementById('filter-unsolved-btn'),
    filterImageBtn: document.getElementById('filter-image-btn'),
    alwaysShowExp: document.getElementById('always-show-explanation'),

    // 메인 카드
    loadingSpinner: document.getElementById('loading-spinner'),
    quizCard: document.getElementById('quiz-card'),
    emptyState: document.getElementById('empty-state'),
    resetFilterBtn: document.getElementById('reset-filter-btn'),

    cardChapter: document.getElementById('card-chapter'),
    cardDiff: document.getElementById('card-diff'),
    cardPage: document.getElementById('card-page'),
    bookmarkToggle: document.getElementById('bookmark-toggle'),
    bookmarkIcon: document.getElementById('bookmark-icon'),

    qNumber: document.getElementById('q-number'),
    qText: document.getElementById('q-text'),
    quizBoxCard: document.getElementById('quiz-box-card'),
    quizImageBox: document.getElementById('quiz-image-box'),
    quizImage: document.getElementById('quiz-image'),
    imageModal: document.getElementById('image-modal'),
    imageModalImg: document.getElementById('image-modal-img'),
    imageModalClose: document.getElementById('image-modal-close'),
    imageModalOverlay: document.getElementById('image-modal-overlay'),
    optionsContainer: document.getElementById('options-container'),

    // 플래시카드 (75선)
    flashcardWrapper: document.getElementById('flashcard-wrapper'),
    flashcard: document.getElementById('flashcard'),
    flashcardFrontTitle: document.getElementById('flashcard-front-title'),
    flashcardFrontQ: document.getElementById('flashcard-front-q'),
    flashcardBackMemo: document.getElementById('flashcard-back-memo'),
    flashcardBackExp: document.getElementById('flashcard-back-exp'),

    // 설명란
    explanationBox: document.getElementById('explanation-box'),
    resultBanner: document.getElementById('result-banner'),
    expText: document.getElementById('exp-text'),
    trapBox: document.getElementById('trap-box'),
    trapText: document.getElementById('trap-text'),
    memoBox: document.getElementById('memo-box'),
    memoText: document.getElementById('memo-text'),
    refFooter: document.getElementById('ref-footer'),
    refText: document.getElementById('ref-text'),
    cardStudyBtn: document.getElementById('card-study-btn'),
    studyLinkBox: document.getElementById('study-link-box'),
    btnStudyLink: document.getElementById('btn-study-link'),
    studyLinkBadge: document.getElementById('study-link-badge'),

    // 하단 페이저
    prevBtn: document.getElementById('prev-btn'),
    nextBtn: document.getElementById('next-btn'),
    currentIndexDisplay: document.getElementById('current-index-display'),
    totalFilterDisplay: document.getElementById('total-filter-display'),

    // 모달
    settingsModal: document.getElementById('settings-modal'),
    closeSettingsBtn: document.getElementById('close-settings-btn'),
    resetAllDataBtn: document.getElementById('reset-all-data-btn'),
    fontBtns: document.querySelectorAll('.font-btn')
  };

  // 3. 로컬 스토리지 로드/저장
  function loadStorage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        state.userStore = Object.assign(state.userStore, parsed);
      }
    } catch (e) {
      console.warn('로컬 저장소 로드 실패:', e);
    }

    // 테마 및 글자 크기 복원
    applyTheme(state.userStore.settings.theme);
    applyFontSize(state.userStore.settings.fontSize);
  }

  function saveStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.userStore));
    } catch (e) {
      console.warn('로컬 저장소 저장 실패:', e);
    }
  }

  // 4. 데이터 비동기 Fetch
  async function initData() {
    try {
      const [mcqRes, boxRes, cardsRes, calcRes] = await Promise.all([
        fetch('questions_mcq.json?v=20261029_v3').then(r => r.json()),
        fetch('questions_box.json?v=20261029_v3').then(r => r.json()),
        fetch('cards_75.json?v=20261029_v3').then(r => r.json()),
        fetch('calc_37.json?v=20261029_v3').then(r => r.json())
      ]);

      state.data.mcq = Array.isArray(mcqRes) ? mcqRes : [];
      state.data.box = Array.isArray(boxRes) ? boxRes : [];
      state.data.cards = Array.isArray(cardsRes) ? cardsRes : [];
      state.data.calc = Array.isArray(calcRes) ? calcRes : [];

      // 뱃지 숫자 갱신
      dom.badgeMcq.textContent = state.data.mcq.length;
      if (dom.badgeBox) dom.badgeBox.textContent = state.data.box.length;
      dom.badgeCards.textContent = state.data.cards.length;
      dom.badgeCalc.textContent = state.data.calc.length;
      state.data.pic = state.data.mcq.filter(q => q.image);
      if (dom.badgePic) dom.badgePic.textContent = state.data.pic.length;

      dom.loadingSpinner.style.display = 'none';

      // 초기 탭 필터링 및 렌더링
      populateChapterFilter();
      applyFilters();
      updateGlobalStats();
    } catch (err) {
      console.error('데이터 로딩 에러:', err);
      dom.loadingSpinner.innerHTML = `
        <span style="font-size: 32px;">⚠️</span>
        <p style="margin-top: 10px; color: #ef4444;">학습 데이터를 불러오는 데 실패했습니다.<br>새로고침을 시도해 주세요.</p>
      `;
    }
  }

  // 5. 과목/단원 필터 드롭다운 구성
  function populateChapterFilter() {
    const list = state.data[state.activeTab] || [];
    const chapters = new Set();

    list.forEach(item => {
      const chap = item.chapter || item.chapter_name || item.type_name || item.part || item.subject;
      if (chap) chapters.add(chap);
    });

    dom.chapterFilter.innerHTML = '<option value="all">전체 과목 / 단원</option>';
    Array.from(chapters).sort().forEach(ch => {
      const opt = document.createElement('option');
      opt.value = ch;
      opt.textContent = ch;
      dom.chapterFilter.appendChild(opt);
    });

    state.filters.chapter = 'all';
  }

  // 6. 필터 적용 로직
  function applyFilters() {
    const tab = state.activeTab;
    const rawList = state.data[tab] || [];

    const targetTab = (tab === 'pic') ? 'mcq' : tab;
    const tabAnswers = (state.userStore.answers && state.userStore.answers[targetTab]) || {};
    const tabBookmarks = (state.userStore.bookmarks && state.userStore.bookmarks[targetTab]) || {};

    state.filteredList = rawList.filter(item => {
      const itemId = getItemId(item);

      // 그림 문제 전용 또는 그림문제 필터
      if ((tab === 'pic' || state.filters.imageOnly) && !item.image) return false;

      // 과목/단원 필터
      if (state.filters.chapter !== 'all') {
        const itemChap = item.chapter || item.chapter_name || item.type_name || item.part || item.subject;
        if (itemChap !== state.filters.chapter) return false;
      }

      // 난이도 필터
      if (state.filters.difficulty !== 'all') {
        if (item.difficulty && item.difficulty !== state.filters.difficulty) return false;
      }

      // 북마크 필터
      if (state.filters.bookmarkOnly) {
        if (!tabBookmarks[itemId]) return false;
      }

      // 오답노트 필터
      if (state.filters.incorrectOnly) {
        const ansInfo = tabAnswers[itemId];
        if (!ansInfo || ansInfo.isCorrect !== false) return false;
      }

      // 안 푼 문제 필터 (풀이 이력이 없는 문제만 표시)
      if (state.filters.unsolvedOnly) {
        const ansInfo = tabAnswers[itemId];
        if (ansInfo) return false;
      }

      return true;
    });

    state.currentIndex = 0;
    renderCurrentQuestion();
    updateNavigation();
  }

  // 고유 ID 추출 헬퍼
  function getItemId(item) {
    return item.id !== undefined ? String(item.id) : (item.chapter_id ? `${item.chapter_id}_${item.id}` : JSON.stringify(item.question));
  }

  // 6.5 요약노트 라운드(study.html?round=...) 자동 매핑 헬퍼
  const STUDY_ROUNDS = {
    '1-1': { round: '1-1', label: '1-1 대상물 선임 기준' },
    '1-2': { round: '1-2', label: '1-2 선임 자격 & 경력' },
    '1-3': { round: '1-3', label: '1-3 소방보조자 선임' },
    '2-1': { round: '2-1', label: '2-1 소방시설 5대 분류' },
    '2-2': { round: '2-2', label: '2-2 벌칙·과태료 금액순' },
    '3-1': { round: '3-1', label: '3-1 건축관계법령' },
    '4-1': { round: '4-1', label: '4-1 연소이론 & 위험물' },
    '4-2': { round: '4-2', label: '4-2 화재이론 & 특수현상' },
    '4-3': { round: '4-3', label: '4-3 소화이론 & 소화약제' },
    '5-1': { round: '5-1', label: '5-1 위험물 안전관리' },
    '5-2': { round: '5-2', label: '5-2 시설기준 & 운반혼재' },
    '5-3': { round: '5-3', label: '5-3 건축구조 & 환기배출' },
    '5-4': { round: '5-4', label: '5-4 전기·가스 안전시설' },
    '6-1': { round: '6-1', label: '6-1 임시소방시설' },
    '6-2': { round: '6-2', label: '6-2 용접·화재감시자' },
    '6-3': { round: '6-3', label: '6-3 특수가연물 기준' },
    '7-1': { round: '7-1', label: '7-1 방재실 개요·위치' },
    '7-2': { round: '7-2', label: '7-2 구조·면적·설비' },
    '7-3': { round: '7-3', label: '7-3 설계도서·운영절차' },
    '8-1': { round: '8-1', label: '8-1 응급처치·사마리아인법' },
    '8-2': { round: '8-2', label: '8-2 심폐소생술(CPR)·가슴압박' },
    '8-3': { round: '8-3', label: '8-3 AED·외상·하임리히' },
    '2-1-1': { round: '2-1-1', label: '2권 1-1 소화기구 구조·점검' },
    '2-1-2': { round: '2-1-2', label: '2권 1-2 옥내소화전 구조·점검' },
    '2-1-3': { round: '2-1-3', label: '2권 1-3 스프링클러설비' },
    '2-1-4': { round: '2-1-4', label: '2권 1-4 가스계·물분무등' },
    '2-1-5': { round: '2-1-5', label: '2권 1-5 옥외소화전설비' },
    '2-2-1': { round: '2-2-1', label: '2권 2-1 수신기 구조·5대시험' },
    '2-2-2': { round: '2-2-2', label: '2권 2-2 감지기원리·경계구역' },
    '2-2-3': { round: '2-2-3', label: '2권 2-3 음향·방송·발신기' },
    '2-2-4': { round: '2-2-4', label: '2권 2-4 피난구조·인명구조' },
    '2-2-5': { round: '2-2-5', label: '2권 2-5 소화활동설비' },
    '2-3-1': { round: '2-3-1', label: '2권 3-1 소방계획 수립원칙·절차' },
    '2-3-2': { round: '2-3-2', label: '2권 3-2 자위소방대 & 초기대응' },
    '2-3-3': { round: '2-3-3', label: '2권 3-3 피난보조 & 업무기록' },
    '2-4-1': { round: '2-4-1', label: '2권 4-1 소방안전교육·훈련' }
  };

  function getStudyRound(item) {
    if (!item) return STUDY_ROUNDS['1-1'];

    const text = [
      item.book || '',
      item.part || '',
      item.chapter || '',
      item.subject || '',
      item.chapter_name || '',
      item.type_name || '',
      item.title || '',
      item.question || ''
    ].join(' ');

    const isBook2 = /제?2권/.test(text) || /(2권|소방시설의 구조|소방계획|자위소방대|소방안전교육)/.test(text);

    // 1) 2권 세부 매핑
    if (isBook2) {
      if (/교육|훈련|무각본|도상훈련|평가표/.test(text)) return STUDY_ROUNDS['2-4-1'];
      if (/피난보조|장애인|업무수행기록|업무기록|서식|작성/.test(text)) return STUDY_ROUNDS['2-3-3'];
      if (/자위소방대|초기대응|대장|부대장|통보연락|초기소화|피난유도|응급구조/.test(text)) return STUDY_ROUNDS['2-3-2'];
      if (/소방계획|사전기획|위험환경|설계및개발|시행|PDCA/.test(text)) return STUDY_ROUNDS['2-3-1'];

      if (/제연|연결송수관|비상콘센트|무선통신|연소방지|소화활동/.test(text)) return STUDY_ROUNDS['2-2-5'];
      if (/유도등|유도표지|피난기구|완강기|구조대|인명구조기구|방열복|공기호흡기|인공소생기/.test(text)) return STUDY_ROUNDS['2-2-4'];
      if (/음향장치|비상방송|시각경보|우선경보|발신기|배선|단독경보/.test(text)) return STUDY_ROUNDS['2-2-3'];
      if (/감지기|경계구역|차동식|정온식|보상식|광전식|이온화식/.test(text)) return STUDY_ROUNDS['2-2-2'];
      if (/수신기|P형|R형|도통시험|화재표시|예비전원|스위치주의/.test(text)) return STUDY_ROUNDS['2-2-1'];

      if (/옥외소화전/.test(text)) return STUDY_ROUNDS['2-1-5'];
      if (/가스계|이산화탄소|할론|할로겐|물분무|포소화|미분무/.test(text)) return STUDY_ROUNDS['2-1-4'];
      if (/스프링클러|유수검지|습식|건식|준비작동식|일제살수/.test(text)) return STUDY_ROUNDS['2-1-3'];
      if (/옥내소화전|펌프시험|성능시험|체절운전|정격운전|릴리프/.test(text)) return STUDY_ROUNDS['2-1-2'];
      if (/소화기|소화약제|능력단위|간이소화/.test(text)) return STUDY_ROUNDS['2-1-1'];
    }

    // 2) 1권 세부 매핑
    if (/응급|CPR|심폐소생술|하임리히|AED|자동심장충격기|사마리아/.test(text)) {
      if (/AED|외상|하임리히|지혈/.test(text)) return STUDY_ROUNDS['8-3'];
      if (/심폐소생술|CPR|가슴압박|인공호흡/.test(text)) return STUDY_ROUNDS['8-2'];
      return STUDY_ROUNDS['8-1'];
    }

    if (/방재실|종합방재실|모니터링/.test(text)) {
      if (/도서|운영|절차/.test(text)) return STUDY_ROUNDS['7-3'];
      if (/구조|면적|설비/.test(text)) return STUDY_ROUNDS['7-2'];
      return STUDY_ROUNDS['7-1'];
    }

    if (/공사장|임시소방시설|용접|화재감시자|특수가연물/.test(text)) {
      if (/특수가연물/.test(text)) return STUDY_ROUNDS['6-3'];
      if (/용접|용단|화재감시자/.test(text)) return STUDY_ROUNDS['6-2'];
      return STUDY_ROUNDS['6-1'];
    }

    if (/위험물|지정수량|탱크|전기|가스|배출|환기/.test(text)) {
      if (/전기|가스|누전|차단/.test(text)) return STUDY_ROUNDS['5-4'];
      if (/건축구조|환기|배출/.test(text)) return STUDY_ROUNDS['5-3'];
      if (/운반|혼재|시설기준/.test(text)) return STUDY_ROUNDS['5-2'];
      return STUDY_ROUNDS['5-1'];
    }

    if (/연소|소화이론|플래시오버|백드래프트|소화약제/.test(text)) {
      if (/소화이론|냉각|질식|억제|소화약제/.test(text)) return STUDY_ROUNDS['4-3'];
      if (/화재이론|특수현상|플래시|백드래フト|롤오버/.test(text)) return STUDY_ROUNDS['4-2'];
      return STUDY_ROUNDS['4-1'];
    }

    if (/건축법|방화구획|방화문|방화셔터|피난계단|내화구조|불연재료/.test(text)) {
      return STUDY_ROUNDS['3-1'];
    }

    if (/벌칙|과태료|5년|3년|1년|500만원|300만원|200만원|100만원/.test(text)) {
      return STUDY_ROUNDS['2-2'];
    }

    if (/소방시설 5대|소화설비|경보설비|피난구조설비|소화용수|소화활동/.test(text)) {
      return STUDY_ROUNDS['2-1'];
    }

    if (/보조자|소방안전관리보조자/.test(text)) return STUDY_ROUNDS['1-3'];
    if (/자격|경력|실무경력|시험/.test(text)) return STUDY_ROUNDS['1-2'];

    return STUDY_ROUNDS['1-1'];
  }

  // 7. 현재 문제 렌더링
  function renderCurrentQuestion() {
    const total = state.filteredList.length;

    if (total === 0) {
      dom.quizCard.style.display = 'none';
      dom.emptyState.style.display = 'block';
      dom.currentIndexDisplay.textContent = '0';
      dom.totalFilterDisplay.textContent = '0';
      const emptyH3 = dom.emptyState.querySelector('h3');
      const emptyDesc = document.getElementById('empty-desc');
      if (state.filters.unsolvedOnly) {
        if (emptyH3) emptyH3.textContent = '축하합니다! 모든 문제를 다 풀었습니다! 🎉';
        if (emptyDesc) emptyDesc.textContent = '현재 탭의 모든 문제를 완료했습니다. 필터를 초기화하여 복습해 보세요.';
      } else {
        if (emptyH3) emptyH3.textContent = '해당 조건의 문제가 없습니다.';
        if (emptyDesc) emptyDesc.textContent = '필터를 변경하거나 전체 문제를 선택해 보세요.';
      }
      return;
    }

    dom.emptyState.style.display = 'none';
    dom.quizCard.style.display = 'flex';

    const item = state.filteredList[state.currentIndex];
    const itemId = getItemId(item);
    const tab = state.activeTab;

    // 메타 정보
    dom.cardChapter.textContent = item.chapter || item.chapter_name || item.type_name || item.part || item.subject || '소방안전';
    dom.cardDiff.textContent = item.difficulty || (item.source ? `출처: ${item.source}` : '실전핵심');
    dom.cardPage.textContent = item.page_ref || (item.book ? item.book : '');
    dom.cardPage.style.display = (item.page_ref || item.book) ? 'inline-block' : 'none';

    // 상단 요약노트 원클릭 링크 갱신
    const studyInfo = getStudyRound(item);
    if (dom.cardStudyBtn) {
      dom.cardStudyBtn.href = `./study.html?round=${studyInfo.round}`;
      dom.cardStudyBtn.title = `[${studyInfo.label}] 1분 족집게 요약노트 새 탭으로 보기`;
    }

    // 북마크 상태
    const targetTab = (tab === 'pic') ? 'mcq' : tab;
    const isBookmarked = !!(state.userStore.bookmarks[targetTab] && state.userStore.bookmarks[targetTab][itemId]);
    dom.bookmarkToggle.classList.toggle('bookmarked', isBookmarked);
    dom.bookmarkIcon.textContent = isBookmarked ? '★' : '☆';

    // 문제 텍스트
    dom.qNumber.textContent = `Q${state.currentIndex + 1}.`;
    dom.qText.textContent = item.question || item.statement || item.title || '';

    // 그림·도면 문제 이미지
    if (dom.quizImageBox && dom.quizImage) {
      if (item.image) {
        dom.quizImageBox.style.display = 'block';
        dom.quizImage.src = item.image;
        dom.quizImage.alt = item.question || '문제 관련 그림';
      } else {
        dom.quizImageBox.style.display = 'none';
        dom.quizImage.src = '';
      }
    }

    // 보기(가, 나, 다) 박스 렌더링
    if (dom.quizBoxCard) {
      if (item.box && Array.isArray(item.box) && item.box.length > 0) {
        dom.quizBoxCard.style.display = 'block';
        let boxHtml = '<div class="box-header"><span>📋</span> [보 기]</div>';
        item.box.forEach(boxLine => {
          const colonIdx = boxLine.indexOf(':');
          if (colonIdx > 0 && colonIdx <= 3) {
            const label = boxLine.substring(0, colonIdx).trim();
            const text = boxLine.substring(colonIdx + 1).trim();
            boxHtml += `
              <div class="box-item">
                <span class="box-badge">${label}</span>
                <span class="box-text">${text}</span>
              </div>
            `;
          } else {
            boxHtml += `<div class="box-item"><span class="box-text">${boxLine}</span></div>`;
          }
        });
        dom.quizBoxCard.innerHTML = boxHtml;
      } else {
        dom.quizBoxCard.style.display = 'none';
        dom.quizBoxCard.innerHTML = '';
      }
    }

    // 기존 풀이 기록 확인
    const history = state.userStore.answers[targetTab] && state.userStore.answers[targetTab][itemId];

    // 탭별 뷰 분기
    if (tab === 'cards') {
      renderCardsView(item, history);
    } else {
      renderMcqView(item, history);
    }

    // 설명란 렌더링
    renderExplanation(item, history);
  }

  // 4지선다 / 보기선택 / 계산 37선 렌더링
  function renderMcqView(item, history) {
    dom.flashcardWrapper.style.display = 'none';
    dom.optionsContainer.style.display = 'flex';
    dom.optionsContainer.className = 'options-container';
    dom.optionsContainer.innerHTML = '';

    const options = item.options || [];
    const correctAnswer = Number(item.answer); // 1-based index

    options.forEach((optText, idx) => {
      const optIdx = idx + 1;
      const btn = document.createElement('button');
      btn.className = 'option-btn';

      btn.innerHTML = `
        <span class="option-idx">${optIdx}</span>
        <span class="option-text">${optText}</span>
      `;

      // 이미 푼 기록이 있는 경우 상태 표시
      if (history) {
        btn.disabled = true;
        if (optIdx === history.selected) {
          btn.classList.add(history.isCorrect ? 'selected-correct' : 'selected-wrong');
        }
        if (!history.isCorrect && optIdx === correctAnswer) {
          btn.classList.add('highlight-correct');
        }
      }

      btn.addEventListener('click', () => {
        handleAnswerSubmit(item, optIdx, correctAnswer);
      });

      dom.optionsContainer.appendChild(btn);
    });
  }

  // 핵심 75선 플래시카드 렌더링
  function renderCardsView(item, history) {
    dom.flashcardWrapper.style.display = 'block';
    dom.flashcard.classList.remove('flipped');

    dom.flashcardFrontTitle.textContent = item.title || item.chapter_name || '핵심 요약';
    dom.flashcardFrontQ.textContent = item.question || '';
    dom.flashcardBackMemo.textContent = item.memo || '💡 핵심 요점을 숙지하세요!';
    dom.flashcardBackExp.textContent = item.explanation || '';

    // 클릭 시 뒤집힘
    dom.flashcard.onclick = () => {
      dom.flashcard.classList.toggle('flipped');
    };

    // 하단에는 4지선다 옵션도 함께 표시하여 자가 테스트 가능하도록 구성
    renderMcqView(item, history);
  }

  // 8. 정답 제출 처리 로직
  function handleAnswerSubmit(item, selectedValue, correctValue) {
    const tab = state.activeTab;
    const targetTab = (tab === 'pic') ? 'mcq' : tab;
    const itemId = getItemId(item);
    const isCorrect = (selectedValue === correctValue);

    if (!state.userStore.answers[targetTab]) {
      state.userStore.answers[targetTab] = {};
    }

    state.userStore.answers[targetTab][itemId] = {
      selected: selectedValue,
      isCorrect: isCorrect,
      timestamp: Date.now()
    };

    saveStorage();
    updateGlobalStats();

    // 화면 즉각 갱신
    renderCurrentQuestion();
  }

  // 9. 설명란(해설) 렌더링
  function renderExplanation(item, history) {
    const showAlways = state.filters.alwaysShowExplanation;

    if (!history && !showAlways) {
      dom.explanationBox.style.display = 'none';
      return;
    }

    dom.explanationBox.style.display = 'block';

    // 결과 배너
    if (history) {
      if (history.isCorrect) {
        dom.resultBanner.className = 'result-banner correct';
        dom.resultBanner.innerHTML = '✅ 정답입니다! 아주 훌륭합니다.';
      } else {
        dom.resultBanner.className = 'result-banner wrong';
        const ansLabel = `${item.answer}번`;
        dom.resultBanner.innerHTML = `❌ 오답입니다. (정답: <strong>${ansLabel}</strong>)`;
      }
    } else {
      dom.resultBanner.className = 'result-banner neutral';
      dom.resultBanner.innerHTML = '💡 [해설 정독 모드] 정답 및 해설이 표시됩니다.';
    }

    // 상세 해설 본문
    dom.expText.textContent = item.explanation || '해당 문제에 등록된 상세 해설이 없습니다.';

    // 함정 팁
    if (item.trap_tip) {
      dom.trapBox.style.display = 'block';
      dom.trapText.textContent = item.trap_tip;
    } else {
      dom.trapBox.style.display = 'none';
    }

    // 암기 메모
    if (item.memo) {
      dom.memoBox.style.display = 'block';
      dom.memoText.textContent = item.memo;
    } else {
      dom.memoBox.style.display = 'none';
    }

    // 출처 안내
    const refInfo = [item.book, item.chapter, item.page_ref].filter(Boolean).join(' · ');
    if (refInfo) {
      dom.refFooter.style.display = 'block';
      dom.refText.textContent = `출처: ${refInfo}`;
    } else {
      dom.refFooter.style.display = 'none';
    }

    // 해설 하단 요약노트 배너 갱신
    const studyInfo = getStudyRound(item);
    if (dom.btnStudyLink && dom.studyLinkBadge) {
      dom.btnStudyLink.href = `./study.html?round=${studyInfo.round}`;
      dom.studyLinkBadge.textContent = studyInfo.label;
      dom.btnStudyLink.title = `[${studyInfo.label}] 1분 족집게 핵심 암기카드 새 탭으로 정독`;
    }
  }

  // 10. 네비게이션 페이저 및 단축키
  function updateNavigation() {
    const total = state.filteredList.length;
    dom.currentIndexDisplay.textContent = total > 0 ? (state.currentIndex + 1) : 0;
    dom.totalFilterDisplay.textContent = total;

    dom.prevBtn.disabled = (state.currentIndex <= 0 || total === 0);
    dom.nextBtn.disabled = (state.currentIndex >= total - 1 || total === 0);
  }

  function goPrev() {
    if (state.currentIndex > 0) {
      state.currentIndex--;
      renderCurrentQuestion();
      updateNavigation();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  function goNext() {
    if (state.currentIndex < state.filteredList.length - 1) {
      state.currentIndex++;
      renderCurrentQuestion();
      updateNavigation();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // 11. 진도율 및 전체 통계 계산
  function updateGlobalStats() {
    let totalItems = 0;
    let answeredItems = 0;
    let correctItems = 0;

    ['mcq', 'box', 'cards', 'calc'].forEach(tab => {
      const list = state.data[tab] || [];
      totalItems += list.length;

      const tabAns = (state.userStore.answers && state.userStore.answers[tab]) || {};
      Object.values(tabAns).forEach(ans => {
        answeredItems++;
        if (ans.isCorrect) correctItems++;
      });
    });

    const percent = totalItems > 0 ? Math.round((answeredItems / totalItems) * 100) : 0;
    const accuracy = answeredItems > 0 ? Math.round((correctItems / answeredItems) * 100) : 0;

    dom.progressPercent.textContent = `${percent}%`;
    dom.progressBarFill.style.width = `${percent}%`;
    dom.answeredCount.textContent = answeredItems;
    dom.totalPoolCount.textContent = totalItems;
    dom.accuracyRate.textContent = answeredItems > 0 ? `${accuracy}%` : '-';
  }

  // 12. 북마크 토글
  function toggleBookmark() {
    if (state.filteredList.length === 0) return;
    const item = state.filteredList[state.currentIndex];
    const itemId = getItemId(item);
    const tab = state.activeTab;
    const targetTab = (tab === 'pic') ? 'mcq' : tab;

    if (!state.userStore.bookmarks[targetTab]) {
      state.userStore.bookmarks[targetTab] = {};
    }

    const current = !!state.userStore.bookmarks[targetTab][itemId];
    if (current) {
      delete state.userStore.bookmarks[targetTab][itemId];
    } else {
      state.userStore.bookmarks[targetTab][itemId] = true;
    }

    saveStorage();
    renderCurrentQuestion();
  }

  // 13. 테마 및 폰트 변경
  function applyTheme(theme) {
    state.userStore.settings.theme = theme;
    if (theme === 'light') {
      document.body.classList.add('light-theme');
      dom.themeBtn.textContent = '☀️';
    } else {
      document.body.classList.remove('light-theme');
      dom.themeBtn.textContent = '🌙';
    }
    saveStorage();
  }

  function applyFontSize(size) {
    state.userStore.settings.fontSize = size;
    document.body.classList.remove('font-small', 'font-large');
    if (size === 'small') document.body.classList.add('font-small');
    if (size === 'large') document.body.classList.add('font-large');

    dom.fontBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.size === size);
    });
    saveStorage();
  }

  // 14. 이벤트 리스너 등록
  function bindEvents() {
    // 탭 전환
    dom.tabs.forEach(tabBtn => {
      if (tabBtn.dataset.tab) {
        tabBtn.addEventListener('click', () => {
          dom.tabs.forEach(t => t.classList.remove('active'));
          tabBtn.classList.add('active');
          state.activeTab = tabBtn.dataset.tab;

          // 필터 초기화 후 재구성
          populateChapterFilter();
          applyFilters();
        });
      }
    });

    // 필터 체인지
    dom.chapterFilter.addEventListener('change', (e) => {
      state.filters.chapter = e.target.value;
      applyFilters();
    });

    dom.diffFilter.addEventListener('change', (e) => {
      state.filters.difficulty = e.target.value;
      applyFilters();
    });

    dom.filterBookmarkBtn.addEventListener('click', () => {
      state.filters.bookmarkOnly = !state.filters.bookmarkOnly;
      dom.filterBookmarkBtn.classList.toggle('active', state.filters.bookmarkOnly);
      applyFilters();
    });

    dom.filterIncorrectBtn.addEventListener('click', () => {
      state.filters.incorrectOnly = !state.filters.incorrectOnly;
      if (state.filters.incorrectOnly && state.filters.unsolvedOnly) {
        state.filters.unsolvedOnly = false;
        dom.filterUnsolvedBtn.classList.remove('active');
      }
      dom.filterIncorrectBtn.classList.toggle('active', state.filters.incorrectOnly);
      applyFilters();
    });

    dom.filterUnsolvedBtn.addEventListener('click', () => {
      state.filters.unsolvedOnly = !state.filters.unsolvedOnly;
      if (state.filters.unsolvedOnly && state.filters.incorrectOnly) {
        state.filters.incorrectOnly = false;
        dom.filterIncorrectBtn.classList.remove('active');
      }
      dom.filterUnsolvedBtn.classList.toggle('active', state.filters.unsolvedOnly);
      applyFilters();
    });
    if (dom.filterImageBtn) {
      dom.filterImageBtn.addEventListener('click', () => {
        state.filters.imageOnly = !state.filters.imageOnly;
        dom.filterImageBtn.classList.toggle('active', state.filters.imageOnly);
        applyFilters();
      });
    }


    dom.alwaysShowExp.addEventListener('change', (e) => {
      state.filters.alwaysShowExplanation = e.target.checked;
      renderCurrentQuestion();
    });

    dom.resetFilterBtn.addEventListener('click', () => {
      state.filters.chapter = 'all';
      state.filters.difficulty = 'all';
      state.filters.bookmarkOnly = false;
      state.filters.incorrectOnly = false;
      state.filters.unsolvedOnly = false;
      dom.chapterFilter.value = 'all';
      dom.diffFilter.value = 'all';
      dom.filterBookmarkBtn.classList.remove('active');
      dom.filterIncorrectBtn.classList.remove('active');
      dom.filterUnsolvedBtn.classList.remove('active');
      state.filters.imageOnly = false;
      if (dom.filterImageBtn) dom.filterImageBtn.classList.remove('active');
      applyFilters();
    });

    
    // 이미지 확대 모달 제어
    if (dom.quizImageBox && dom.imageModal) {
      dom.quizImageBox.addEventListener('click', () => {
        if (dom.quizImage && dom.quizImage.src) {
          dom.imageModalImg.src = dom.quizImage.src;
          dom.imageModal.style.display = 'flex';
        }
      });
    }

    if (dom.imageModalClose) {
      dom.imageModalClose.addEventListener('click', () => {
        dom.imageModal.style.display = 'none';
      });
    }

    if (dom.imageModalOverlay) {
      dom.imageModalOverlay.addEventListener('click', () => {
        dom.imageModal.style.display = 'none';
      });
    }

    // 북마크 클릭
    dom.bookmarkToggle.addEventListener('click', toggleBookmark);

    // 이전 / 다음
    dom.prevBtn.addEventListener('click', goPrev);
    dom.nextBtn.addEventListener('click', goNext);

    // 키보드 단축키
    window.addEventListener('keydown', (e) => {
      if (dom.settingsModal.style.display === 'flex') return;
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === 'ArrowRight') goNext();
      if (['1', '2', '3', '4'].includes(e.key)) {
        const optionBtns = dom.optionsContainer.querySelectorAll('.option-btn');
        const targetBtn = optionBtns[parseInt(e.key, 10) - 1];
        if (targetBtn && !targetBtn.disabled) targetBtn.click();
      }
    });

    // 테마 토글
    dom.themeBtn.addEventListener('click', () => {
      const nextTheme = state.userStore.settings.theme === 'light' ? 'dark' : 'light';
      applyTheme(nextTheme);
    });

    // 모달 제어
    dom.settingsBtn.addEventListener('click', () => {
      dom.settingsModal.style.display = 'flex';
    });
    dom.closeSettingsBtn.addEventListener('click', () => {
      dom.settingsModal.style.display = 'none';
    });
    dom.settingsModal.addEventListener('click', (e) => {
      if (e.target === dom.settingsModal) dom.settingsModal.style.display = 'none';
    });

    // 폰트 크기
    dom.fontBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        applyFontSize(btn.dataset.size);
      });
    });

    // 데이터 초기화
    dom.resetAllDataBtn.addEventListener('click', () => {
      if (confirm('정말로 모든 학습 진도, 오답노트, 북마크 기록을 삭제하시겠습니까?')) {
        localStorage.removeItem(STORAGE_KEY);
        state.userStore.answers = {};
        state.userStore.bookmarks = {};
        saveStorage();
        updateGlobalStats();
        renderCurrentQuestion();
        dom.settingsModal.style.display = 'none';
        alert('모든 학습 데이터가 초기화되었습니다.');
      }
    });
  }

  // 실행 진입점
  document.addEventListener('DOMContentLoaded', () => {
    loadStorage();
    bindEvents();
    initData();
  });
})();
