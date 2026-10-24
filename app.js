/**
 * 소방안전관리자 1급 마스터 - 메인 컨트롤러 (Vanilla JS)
 */

(function () {
  'use strict';

  // 1. 상태(State) 관리
  const state = {
    activeTab: 'mcq', // 'mcq' | 'ox' | 'cards' | 'calc'
    data: {
      mcq: [],
      ox: [],
      cards: [],
      calc: []
    },
    filteredList: [],
    currentIndex: 0,
    filters: {
      chapter: 'all',
      difficulty: 'all',
      bookmarkOnly: false,
      incorrectOnly: false,
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
    badgeOx: document.getElementById('badge-ox'),
    badgeCards: document.getElementById('badge-cards'),
    badgeCalc: document.getElementById('badge-calc'),

    // 필터
    chapterFilter: document.getElementById('chapter-filter'),
    diffFilter: document.getElementById('diff-filter'),
    filterBookmarkBtn: document.getElementById('filter-bookmark-btn'),
    filterIncorrectBtn: document.getElementById('filter-incorrect-btn'),
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
      const [mcqRes, oxRes, cardsRes, calcRes] = await Promise.all([
        fetch('questions_mcq.json').then(r => r.json()),
        fetch('questions_ox.json').then(r => r.json()),
        fetch('cards_75.json').then(r => r.json()),
        fetch('calc_37.json').then(r => r.json())
      ]);

      state.data.mcq = Array.isArray(mcqRes) ? mcqRes : [];
      state.data.ox = Array.isArray(oxRes) ? oxRes : [];
      state.data.cards = Array.isArray(cardsRes) ? cardsRes : [];
      state.data.calc = Array.isArray(calcRes) ? calcRes : [];

      // 뱃지 숫자 갱신
      dom.badgeMcq.textContent = state.data.mcq.length;
      dom.badgeOx.textContent = state.data.ox.length;
      dom.badgeCards.textContent = state.data.cards.length;
      dom.badgeCalc.textContent = state.data.calc.length;

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

    const tabAnswers = (state.userStore.answers && state.userStore.answers[tab]) || {};
    const tabBookmarks = (state.userStore.bookmarks && state.userStore.bookmarks[tab]) || {};

    state.filteredList = rawList.filter(item => {
      const itemId = getItemId(item);

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

  // 7. 현재 문제 렌더링
  function renderCurrentQuestion() {
    const total = state.filteredList.length;

    if (total === 0) {
      dom.quizCard.style.display = 'none';
      dom.emptyState.style.display = 'block';
      dom.currentIndexDisplay.textContent = '0';
      dom.totalFilterDisplay.textContent = '0';
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

    // 북마크 상태
    const isBookmarked = !!(state.userStore.bookmarks[tab] && state.userStore.bookmarks[tab][itemId]);
    dom.bookmarkToggle.classList.toggle('bookmarked', isBookmarked);
    dom.bookmarkIcon.textContent = isBookmarked ? '★' : '☆';

    // 문제 텍스트
    dom.qNumber.textContent = `Q${state.currentIndex + 1}.`;
    dom.qText.textContent = item.question || item.statement || item.title || '';

    // 기존 풀이 기록 확인
    const history = state.userStore.answers[tab] && state.userStore.answers[tab][itemId];

    // 탭별 뷰 분기
    if (tab === 'cards') {
      renderCardsView(item, history);
    } else if (tab === 'ox') {
      renderOxView(item, history);
    } else {
      renderMcqView(item, history);
    }

    // 설명란 렌더링
    renderExplanation(item, history);
  }

  // 4지선다 / 계산 37선 렌더링
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

  // 스피드 OX 렌더링
  function renderOxView(item, history) {
    dom.flashcardWrapper.style.display = 'none';
    dom.optionsContainer.style.display = 'grid';
    dom.optionsContainer.className = 'ox-buttons-grid';
    dom.optionsContainer.innerHTML = '';

    const isTrueAnswer = (item.answer === true || item.answer === 'O' || item.answer === 1);

    const oxData = [
      { text: '⭕ 그렇다', val: true, class: 'ox-btn-o' },
      { text: '❌ 아니다', val: false, class: 'ox-btn-x' }
    ];

    oxData.forEach(btnInfo => {
      const btn = document.createElement('button');
      btn.className = `ox-btn ${btnInfo.class}`;
      btn.innerHTML = `
        <span>${btnInfo.val ? 'O' : 'X'}</span>
        <span class="ox-btn-sub">${btnInfo.text}</span>
      `;

      if (history) {
        btn.disabled = true;
        if (history.selected === btnInfo.val) {
          btn.classList.add(history.isCorrect ? 'selected-correct' : 'selected-wrong');
        }
      }

      btn.addEventListener('click', () => {
        handleAnswerSubmit(item, btnInfo.val, isTrueAnswer);
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
    const itemId = getItemId(item);
    const isCorrect = (selectedValue === correctValue);

    if (!state.userStore.answers[tab]) {
      state.userStore.answers[tab] = {};
    }

    state.userStore.answers[tab][itemId] = {
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
        const ansLabel = (state.activeTab === 'ox')
          ? (item.answer ? 'O (그렇다)' : 'X (아니다)')
          : `${item.answer}번`;
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

    ['mcq', 'ox', 'cards', 'calc'].forEach(tab => {
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

    if (!state.userStore.bookmarks[tab]) {
      state.userStore.bookmarks[tab] = {};
    }

    const current = !!state.userStore.bookmarks[tab][itemId];
    if (current) {
      delete state.userStore.bookmarks[tab][itemId];
    } else {
      state.userStore.bookmarks[tab][itemId] = true;
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
      dom.filterIncorrectBtn.classList.toggle('active', state.filters.incorrectOnly);
      applyFilters();
    });

    dom.alwaysShowExp.addEventListener('change', (e) => {
      state.filters.alwaysShowExplanation = e.target.checked;
      renderCurrentQuestion();
    });

    dom.resetFilterBtn.addEventListener('click', () => {
      state.filters.chapter = 'all';
      state.filters.difficulty = 'all';
      state.filters.bookmarkOnly = false;
      state.filters.incorrectOnly = false;
      dom.chapterFilter.value = 'all';
      dom.diffFilter.value = 'all';
      dom.filterBookmarkBtn.classList.remove('active');
      dom.filterIncorrectBtn.classList.remove('active');
      applyFilters();
    });

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
