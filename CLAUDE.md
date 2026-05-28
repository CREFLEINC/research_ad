# Anomaly Detection 연구 프로젝트

딥러닝 기술을 활용한 머신 비전 분야 Anomaly Detection 연구·제품화 프로젝트.

## 하네스: Anomaly Detection (제조 머신 비전) 연구

**목표:** 연구 단계의 Anomaly Detection 기술을 실제 제조 생산 현장에서 활용 가능한 제품화 수준으로 끌어올림.

**트리거:** Anomaly Detection, AD 연구, 이상 탐지, 결함 검출, 머신 비전 검사 관련 작업 요청 시 `anomaly-research-orchestrator` 스킬을 사용한다. 단순 질문은 직접 응답 가능.

**연구 활동 규칙 (모든 작업에서 준수):**
1. **사용자 참여형 연구 활동** — 모든 주요 안건은 정리하여 사용자에게 제시, 사용자가 의사결정한다. 연속 진행 금지.
2. **객관적 평가 기반 의사결정** — 수치적 객관성 필수. 확률적 의사결정은 그 확률의 근거를 서술적으로 설명.
3. **중복 구현 방지** — 검증된 오픈소스가 있으면 직접 구현하지 않는다. 단, 정확성 검증은 필수.

**최종 결과물:**
1. 연구 계획안 — `_workspace/02_validation/validation_report.md` + `_workspace/03_research/consolidated_proposals.md` (HTML: `reports/phases/02_validation.html`, `03_consolidated.html`)
2. 연구 과정 노트 — `_workspace/03_research/discussion_log.md` + `critique_notes.md`
3. 검증 가능한 구현체 — `code/` (HTML 결과: `reports/phases/04_implementation.html`)
4. 5페이지 이내 논문 — `_workspace/05_paper/paper.md` (HTML: `reports/phases/05_paper.html`)
5. 학습/설명 자료 — `reports/learning/NN_topic.html` (해당 시)

**산출 형식 정책:**
- 사용자에게 "보고"하는 깊이 있는 정리 자료 → **HTML** (`reports/` 하위, `base.css` + KaTeX)
- 사용자 의사결정 / 게이트 / 상태 알림 → **채팅 마크다운** (현행 유지)
- 에이전트 간 작업 파일 (`_workspace/**`) → 마크다운 유지
- 상세 규칙: `.claude/skills/html-reporting/SKILL.md`

**변경 이력:**

| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-05-25 | 초기 구성 — 6 에이전트 + 6 스킬 + 오케스트레이터 | 전체 | 신규 하네스 구축 |
| 2026-05-26 | HTML 보고 정책 신설 — `html-reporting` 스킬 추가, `reports/` 구조 정의, base.css + KaTeX 템플릿 | skills/html-reporting, reports/_assets, tech-surveyor/tech-validator/developer 에이전트, anomaly-research-orchestrator 스킬 | 사용자가 "보고" 산출물을 HTML로 받기를 원함 (게이트/상태는 채팅 유지) |
| 2026-05-27 | KaTeX 로딩 안정화 — 공유 `katex-loader.js` 신설, SRI 해시 제거, 기존 7개 HTML 일괄 갱신 | reports/_assets/katex-loader.js, reports/{learning,qna,concepts}/*.html, html-reporting 스킬 | SRI 해시 오타로 KaTeX 스크립트 로드 실패 → 수식이 raw LaTeX로 표시되던 문제 해결 |
| 2026-05-28 | EfficientAD 파생 자료 2개 카테고리로 통합 — `concepts/01` (KD 역사 + Teacher 적응) + `concepts/02_kl_and_cross_entropy` (CE/KL 완전 가이드). 원본 5개 삭제 (`concepts/02,03` + `qna/04,05,06`) | concepts/01, concepts/02_kl_and_cross_entropy, index.html | 학습 자료가 분산되어 일관된 참조 어려움 → 두 통합본으로 단순화 |
