---
name: anomaly-research-orchestrator
description: "딥러닝 기반 Anomaly Detection (제조 머신 비전) 연구 워크플로우를 조율하는 통합 오케스트레이터. 기술 조사 → 한계 검증 → 3인 연구팀 토론 → 구현·검증 → 논문 초안의 전 과정을 사용자 의사결정 게이트와 함께 진행. '이상 탐지 연구', 'AD 연구', '결함 검출 연구', '머신 비전 검사', '연구 시작', '연구 계획' 요청 시 반드시 사용. 후속 작업: 조사 보완, 검증 재실행, 아이디어 재논의, 구현 추가, 논문 수정, 결과 개선, 부분 재실행, 이전 결과 기반 작업 요청 시에도 반드시 이 스킬을 사용."
---

# Anomaly Research Orchestrator

딥러닝 기반 Anomaly Detection (제조 머신 비전) 연구를 위한 6 에이전트 하네스의 통합 오케스트레이터.

## 실행 모드: 하이브리드

| Phase | 모드 | 이유 |
|-------|------|------|
| Phase 1 (조사) | 서브 에이전트 | 단발 자료 수집, 팀 통신 불필요 |
| Phase 2 (검증) | 서브 에이전트 | 단일 검증자, 다른 에이전트와 실시간 협업 불필요 |
| Phase 3 (연구팀 토론) | **에이전트 팀** | 3명의 토론·합의가 본질적 가치 |
| Phase 4 (구현·검증) | 서브 에이전트 | 단일 개발자가 독립 수행 |
| Phase 5 (논문 초안) | 서브 에이전트 | 단일 작성자 |

각 Phase 사이에 **사용자 의사결정 게이트**가 있다 (연구 규칙 1: 사용자 참여형).

## 에이전트 구성

| 에이전트 | subagent_type | 역할 | 사용 스킬 | 작업 파일 (MD) | 사용자 보고 (HTML) |
|---------|--------------|------|----------|--------------|------------------|
| tech-surveyor | tech-surveyor | 기술 조사·정리 | tech-survey + html-reporting | `_workspace/01_survey/survey_report.md` | `reports/phases/01_survey.html` |
| tech-validator | tech-validator | 검증 + 한계 도출 | tech-validation + html-reporting | `_workspace/02_validation/validation_report.md` | `reports/phases/02_validation.html` |
| researcher-novelty | researcher-novelty | 창의 제안 | research-ideation | `_workspace/03_research/ideas_novelty.md` | (개별 HTML 없음 — 통합본만) |
| researcher-pragmatist | researcher-pragmatist | 적용성 검토 | research-ideation | `_workspace/03_research/ideas_pragmatist.md` | (개별 HTML 없음 — 통합본만) |
| researcher-critic | researcher-critic | 비판·검증 | research-ideation | `_workspace/03_research/critique_notes.md` | (개별 HTML 없음 — 통합본만) |
| **(메인)** | — | 합의서 통합 | (오케스트레이터) | `_workspace/03_research/consolidated_proposals.md` | `reports/phases/03_consolidated.html` |
| developer | developer | 구현·검증 | implementation-and-verification + html-reporting | `_workspace/04_implementation/results.md` + `code/` | `reports/phases/04_implementation.html` |
| **(메인)** | — | 논문 초안 | paper-drafting + html-reporting | `_workspace/05_paper/paper.md` | `reports/phases/05_paper.html` |
| **(메인)** | — | 학습/설명 자료 | html-reporting | (없음, HTML이 원본) | `reports/learning/NN_topic.html` |

### HTML 보고서 정책 (요약)
- **사용자가 차분히 읽는 "보고" 성격 산출물 → HTML** (각 Phase 보고서, 학습 자료)
- **사용자 의사결정 / 게이트 / 상태 알림 → 채팅 마크다운** (현행 유지)
- **에이전트 간 작업 파일 (`_workspace/**`) → 마크다운 유지** (토큰 효율)
- 상세 규칙: `html-reporting` 스킬 참조

## 모든 Agent 호출은 `model: "opus"` 필수.

## 워크플로우

### Phase 0: 컨텍스트 확인

기존 산출물 존재 여부를 확인하여 실행 모드 결정:

1. `_workspace/` 디렉토리 존재 여부 확인
2. 실행 모드 결정:
   - **미존재** → 초기 실행 (Phase 1부터 전체)
   - **존재 + 사용자가 부분 수정 요청** → 부분 재실행 (해당 Phase만)
   - **존재 + 새 입력 제공** → 새 실행. 기존 `_workspace/`를 `_workspace_{YYYYMMDD_HHMMSS}/`로 이동 후 Phase 1
3. 부분 재실행 시 이전 산출물 경로를 해당 에이전트의 프롬프트에 포함

### Phase 1: 기술 조사

**실행 모드:** 서브 에이전트

1. `_workspace/01_survey/` 디렉토리 생성
2. 사용자에게 조사 범위 확인 — 기본값: "딥러닝 기반 머신 비전 Anomaly Detection 전반 (비지도/지도/few-shot 포함)"
3. `Agent` 도구 호출:
   ```
   Agent(
     subagent_type: "tech-surveyor",
     model: "opus",
     description: "AD 기술 조사",
     prompt: "tech-survey 스킬을 사용하여 조사 보고서를 `_workspace/01_survey/survey_report.md`에 작성하라. 조사 범위: <사용자 확인 범위>"
   )
   ```
4. **사용자 게이트 1**: 보고서 핵심을 요약하여 제시 → 사용자가 (a) 진행 (b) 조사 보완 요청 중 선택

### Phase 2: 기술 검증 및 한계 도출

**실행 모드:** 서브 에이전트

1. `_workspace/02_validation/` 디렉토리 생성
2. `Agent` 도구 호출:
   ```
   Agent(
     subagent_type: "tech-validator",
     model: "opus",
     description: "기술 검증 + 한계 도출",
     prompt: "tech-validation 스킬을 사용하여 `_workspace/01_survey/survey_report.md`를 입력으로 검증 보고서를 `_workspace/02_validation/validation_report.md`에 작성하라. Top-3 한계점을 반드시 도출하라."
   )
   ```
3. **사용자 게이트 2**: Top-3 한계와 분류(blocker/mitigable/acceptable)를 표로 제시 → 사용자가 (a) Top-3 그대로 (b) 우선순위 변경 (c) 다른 한계 추가 중 선택

### Phase 3: 3인 연구팀 토론 (핵심)

**실행 모드:** 에이전트 팀

1. `_workspace/03_research/` 디렉토리 생성
2. 팀 생성:
   ```
   TeamCreate(
     team_name: "anomaly-research-team",
     members: [
       { name: "novelty", agent_type: "researcher-novelty", model: "opus",
         prompt: "research-ideation 스킬을 따른다. 단계 1: `_workspace/02_validation/validation_report.md`의 Top-3 한계를 읽고 5개 이상의 후보 아이디어를 `_workspace/03_research/ideas_novelty.md`에 작성. 작성 후 pragmatist, critic에게 SendMessage로 검토 요청." },
       { name: "pragmatist", agent_type: "researcher-pragmatist", model: "opus",
         prompt: "research-ideation 스킬을 따른다. novelty 작성 완료 알림을 받으면 `ideas_novelty.md`를 읽고 각 아이디어를 현장 적용 제약으로 평가하여 `_workspace/03_research/ideas_pragmatist.md`에 작성. 단순 대안 1개씩 제시." },
       { name: "critic", agent_type: "researcher-critic", model: "opus",
         prompt: "research-ideation 스킬을 따른다. novelty와 pragmatist 산출물이 나오면 모두 비판적으로 검증하여 `_workspace/03_research/critique_notes.md`에 작성. 토론 후 `residual_risks.md` 작성." }
     ]
   )
   ```
3. 작업 등록:
   ```
   TaskCreate(tasks: [
     { title: "초안 작성 - novelty", description: "5개 이상 아이디어 발의", assignee: "novelty" },
     { title: "초안 검토 - pragmatist", description: "novelty 초안 적용성 평가", assignee: "pragmatist", depends_on: ["초안 작성 - novelty"] },
     { title: "비판 - critic", description: "두 초안 모두에 비판", assignee: "critic", depends_on: ["초안 검토 - pragmatist"] },
     { title: "토론 라운드 (최대 3)", description: "discussion_log.md 공동 작성, SendMessage 사용. critic이 모든 새 아이디어에 최소 1회 비판.", assignee: "all" },
     { title: "평가 매트릭스", description: "단계 3의 표 작성", assignee: "critic" },
     { title: "합의서 작성", description: "consolidated_proposals.md 공동 정리", assignee: "all" }
   ])
   ```
4. 리더(오케스트레이터) 모니터링:
   - 팀원 유휴 알림 수신 → 진행 상황 확인
   - 합의 지연 시 `SendMessage`로 라운드 종료 권고
   - 토론 라운드는 최대 3회 — 초과 시 "이견 보존" 처리
5. 팀 종료: `TeamDelete`
6. **사용자 게이트 3**: 합의서 요약 + 평가 매트릭스 + 이견 보존 항목을 제시 → 사용자가 (a) 채택안 확정 (b) 일부 재논의 (c) 우선순위 변경

### Phase 4: 구현 및 검증

**실행 모드:** 서브 에이전트

1. `_workspace/04_implementation/` 및 `code/` 디렉토리 생성
2. 사용자 의사결정 기반으로 구현 대상 선택
3. `Agent` 도구 호출:
   ```
   Agent(
     subagent_type: "developer",
     model: "opus",
     description: "선택된 안 구현·검증",
     prompt: "implementation-and-verification 스킬을 사용하여 `_workspace/03_research/consolidated_proposals.md`의 채택안 중 <사용자 선택 ID>를 구현하고 MVTec AD에서 베이스라인(PatchCore) 대비 비교 검증. 결과를 `_workspace/04_implementation/results.md`에 보고. 가능한 한 anomalib 등 오픈소스 활용."
   )
   ```
4. **사용자 게이트 4**: 결과 표(베이스라인 vs 제안)와 한계 분석 제시 → 사용자가 (a) 논문 단계 (b) 개선 재시도 (c) 추가 안 구현

### Phase 5: 논문 초안 작성

1. `_workspace/05_paper/` 디렉토리 생성
2. 메인이 `paper-drafting` 스킬을 직접 따르며 `paper.md`를 5페이지 이내로 작성
3. **사용자 게이트 5**: 초안 제시 → 사용자가 (a) 승인 (b) 수정 요청

### Phase 6: 최종 정리

다음 최종 산출물을 점검하고 사용자에게 위치를 보고:

| # | 산출물 | 작업 파일 (MD) | 사용자 보고 (HTML) |
|---|--------|---------------|------------------|
| 1 | 연구 계획안 | `_workspace/02_validation/validation_report.md` + `_workspace/03_research/consolidated_proposals.md` | `reports/phases/02_validation.html` + `reports/phases/03_consolidated.html` |
| 2 | 연구 과정 노트 | `_workspace/03_research/discussion_log.md` + `_workspace/03_research/critique_notes.md` | (개별 HTML 없음, 03_consolidated.html에 통합 요약) |
| 3 | 검증 가능한 구현체 | `code/` | `reports/phases/04_implementation.html` |
| 4 | 5페이지 이내 논문 | `_workspace/05_paper/paper.md` | `reports/phases/05_paper.html` |
| 5 | 학습/설명 자료 | (없음) | `reports/learning/NN_topic.html` (해당 시) |

`_workspace/` 전체를 보존 (감사 추적). `reports/` 도 보존 (사용자 가독본).

## 데이터 흐름

```
[메인] → tech-surveyor(서브) → survey_report.md
       → [사용자 게이트 1]
       → tech-validator(서브) → validation_report.md
       → [사용자 게이트 2]
       → TeamCreate(novelty, pragmatist, critic) ─SendMessage→ 토론
                                                  └→ consolidated_proposals.md
       → TeamDelete
       → [사용자 게이트 3]
       → developer(서브) → code/ + results.md
       → [사용자 게이트 4]
       → 메인이 paper-drafting → paper.md
       → [사용자 게이트 5]
```

## 사용자 게이트 작성 형식

각 게이트는 다음 형식으로 사용자에게 제시:

```
## 사용자 의사결정 요청 (게이트 N)

### 현재까지의 결론
- (수치적 객관성을 갖춘 요약)

### 연구 에이전트들의 의견
- {에이전트}: {의견}

### 의사결정 옵션
- (a) <옵션> — 예상 결과
- (b) <옵션> — 예상 결과
- (c) <옵션> — 예상 결과

### 추천 (수치 근거 포함)
- 옵션 (X) 추천. 근거: ...
```

## 연구 활동 규칙 적용 (반드시 준수)

1. **사용자 참여형**: 모든 Phase 사이에 사용자 게이트가 있어야 한다. 게이트 없이 연속 진행 금지
2. **객관적 평가**: 모든 의사결정 옵션의 결과 예측은 수치 또는 확률+서술 근거를 동반
3. **중복 구현 방지**: 모든 에이전트 프롬프트에 "기존 오픈소스 우선 활용" 명시. developer는 사전 점검 결과를 `pre_check.md`로 보고

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| 서브 에이전트 1회 실패 | 1회 재시도, 재실패 시 결과 누락 명시 후 사용자에게 보고 |
| 연구팀 토론 합의 실패 | "이견 보존" 섹션으로 처리, 사용자에게 결정 위임 |
| 연구팀 중 1명 중지 | 리더가 SendMessage로 상태 확인, 재시작 또는 나머지로 진행 |
| 구현 학습 자원 부족 | 사전학습 가중치 또는 더 작은 backbone으로 대체 + 변경 사항 명시 |
| 데이터셋 접근 불가 | 합성 데이터로 대체 후 한계 명시 |

## 테스트 시나리오

### 정상 흐름
1. 사용자 "AD 연구 시작해줘"
2. Phase 1: tech-surveyor가 30분 내 survey_report.md 작성 → 게이트 1
3. 사용자가 Top-3 한계 확정 (게이트 2)
4. Phase 3: 3인 팀이 토론 2라운드 후 consolidated_proposals.md 작성 → 게이트 3
5. 사용자가 채택안 A 선택 → developer가 anomalib 기반 구현 → results.md → 게이트 4
6. 사용자가 논문 진행 승인 → paper.md → 게이트 5
7. 최종 산출물 4종 위치 보고

### 에러 흐름
1. Phase 3에서 critic이 모든 아이디어를 부정 → 합의 실패
2. 리더가 SendMessage로 라운드 종료 권고, "이견 보존" 섹션 작성
3. 사용자에게 옵션 제시: (a) novelty의 차선책 진행 (b) 새 조사 라운드 (c) 중단
4. 사용자 선택에 따라 진행

## 후속 작업 처리

이전 산출물이 있을 때 사용자가:
- "조사 보완" → Phase 1 부분 재실행 (이전 보고서 입력으로 포함)
- "다시 토론" → Phase 3 재실행, 이전 토론 로그 보존
- "다른 안 구현" → Phase 4만 재실행, 새 실험 디렉토리
- "논문 수정" → Phase 5 재작성

후속 작업도 사용자 게이트는 동일하게 유지.
