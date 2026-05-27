---
name: html-reporting
description: "사용자에게 정보를 정리해서 '보고'하는 산출물을 HTML로 만드는 절차. 사용자 게이트(의사결정 요청)·단순 계획 확인·진행 상태 알림은 채팅 마크다운 그대로 유지하고, 본 스킬은 '깊이 있게 정리된 보고/학습/분석 문서'에만 적용한다. '리포트 작성', '학습 자료', '보고서', '정리 자료' 요청 시 사용. 후속 작업: 보고서 갱신, 새 모델 학습 자료 추가 시에도 사용."
---

# HTML Reporting — 사용자 보고서 HTML 출력 절차

본 스킬은 본 프로젝트의 **사용자 가독성 정책**을 정의한다.

## 어떤 산출물을 HTML로?

| 산출물 유형 | 출력 형식 | 사유 |
|------------|----------|------|
| **에이전트 보고서 (survey / validation / consolidated / results / paper)** | HTML (+ 마크다운 소스 유지) | 정보 정리·표·수식·코드를 포함한 "보고" 성격 |
| **학습/설명 자료 (모델 해설, 개념 정리, 비교 분석)** | HTML | "보고" 성격 — 차분히 읽음 |
| **사용자 의사결정 요청 (게이트, 옵션 (a)(b)(c))** | 채팅 마크다운 | 빠른 상호작용용 |
| **진행 상태/오류 알림** | 채팅 마크다운 | 짧고 즉시 응답 |
| **단순 계획 확인 (조사 범위, 우선순위 선택)** | 채팅 마크다운 | 의사결정 흐름의 일부 |
| **에이전트 간 작업 파일 (_workspace/**)** | 마크다운 유지 | 내부 통신용, 토큰 효율 |

## 디렉토리 구조

```
reports/
├── _assets/
│   └── base.css                       # 공통 스타일 (모든 HTML이 참조)
├── phases/                            # Phase 산출물 HTML 버전
│   ├── 01_survey.html                 # tech-surveyor 보고서
│   ├── 02_validation.html             # tech-validator 보고서
│   ├── 03_consolidated.html           # 연구팀 합의서
│   ├── 04_implementation.html         # developer 결과
│   └── 05_paper.html                  # 논문 초안 HTML 미리보기
└── learning/                          # 학습/설명 자료
    ├── 01_patchcore.html
    ├── 02_efficient_ad.html
    ├── 03_musc.html
    ├── 04_anomaly_clip.html
    ├── 05_dinomaly.html
    └── ...
```

## HTML 작성 원칙

### 1. 자족적 (Self-contained)
- 외부 빌드 도구 불필요
- CSS는 `reports/_assets/base.css` 단일 파일 참조
- 수식은 KaTeX CDN으로 렌더 (오프라인 시 텍스트 폴백)
- 코드 syntax 하이라이트 미사용 (단색, 가독성 우선)

### 2. 일관성
- 모든 HTML은 `<link rel="stylesheet" href="../_assets/base.css">` (또는 적절한 상대경로)로 base.css 참조
- 문서 머리에 `<header class="doc-header">` 사용 — crumb + h1 + meta
- 본문 섹션은 `<section>` + `<h2>` 단위
- 표는 `<table>`, 코드는 `<pre><code>`
- 콜아웃은 `.callout` (기본/`warn`/`danger`/`ok`)

### 3. 구조화된 콘텐츠
- **표**: 비교/정리는 항상 표로 — 수치 컬럼은 `class="num"` 우측 정렬
- **단계별 절차**: `<ol class="steps">` — Step 1, Step 2... 자동 번호
- **2열 비교** (장점/단점 등): `<div class="cols">`
- **태그/뱃지**: `<span class="tag">` 또는 변형 (`warn`/`ok`/`danger`)

### 4. 수식
- `<script>` 태그로 KaTeX CDN 자동 렌더 (HTML 머리에 포함)
- inline: `$ ... $`, display: `$$ ... $$`

### 5. 한국어 친화
- `<html lang="ko">` 명시
- 폰트 stack에 Pretendard, Noto Sans KR, Apple SD Gothic Neo 포함 (base.css에 있음)

## 표준 HTML 골격

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{문서 제목} — Anomaly Detection 연구</title>
<link rel="stylesheet" href="../_assets/base.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
</head>
<body>
<main>

<header class="doc-header">
  <div class="crumb">{breadcrumb 카테고리}</div>
  <h1>{문서 제목}</h1>
  <div class="meta">
    <span>{날짜}</span>
    <span>{Phase/출처}</span>
    <span>{한 줄 요약}</span>
  </div>
</header>

<section>
<h2>1. {섹션 제목}</h2>
...
</section>

<footer class="doc-footer">
<p>작성: <code>{스킬/에이전트 이름}</code> · 작성일 {YYYY-MM-DD} · 위치 <code>reports/.../{파일명}</code></p>
<p>참조: <code>{관련 마크다운 소스 경로}</code></p>
</footer>

</main>
</body>
</html>
```

## 워크플로우: 마크다운 → HTML 변환

본 스킬은 두 가지 모드로 사용:

### 모드 1. 에이전트가 직접 HTML도 생성
에이전트의 출력 프로토콜에 다음을 명시:
- 마크다운 작업 파일은 `_workspace/`에 저장 (기존 그대로)
- 사용자 보고용 HTML은 `reports/phases/<phase>_<topic>.html`에 작성
- HTML은 위 표준 골격을 따르고 base.css를 참조

### 모드 2. 오케스트레이터가 변환
학습 자료 / 사후 정리 / 짧은 보고는 오케스트레이터(메인 Claude)가 마크다운 콘텐츠를 직접 HTML로 작성한다.

## 콘텐츠 변환 규칙 (마크다운 → HTML)

| Markdown | HTML |
|----------|------|
| `# 제목` | `<h1>` (header.doc-header 내) |
| `## 섹션` | `<h2>` + `<section>` 시작 |
| `### 부섹션` | `<h3>` |
| `**굵게**` | `<strong>` |
| `*기울임*` | `<em>` |
| `` `코드` `` | `<code>` |
| ```` ```python ... ``` ```` | `<pre><code class="language-python">...</code></pre>` |
| `$수식$` / `$$수식$$` | 그대로 (KaTeX 자동 렌더) |
| 표 (마크다운) | `<table>` 변환, 수치 컬럼은 `class="num"` 추가 |
| `> 인용` | `<div class="callout">...</div>` |
| `> [!WARN]` 또는 ⚠ | `<div class="callout warn">` |
| `> [!OK]` 또는 ✅ | `<div class="callout ok">` |
| `> [!DANGER]` 또는 🔥 | `<div class="callout danger">` |

## 무엇을 HTML로 만들지 않는가 (재확인)

- ❌ 사용자 게이트의 옵션 표 (a/b/c) — 채팅 마크다운
- ❌ 진행 상태 ("작업 중", "완료") — 채팅 마크다운
- ❌ 짧은 오류 보고 — 채팅 마크다운
- ❌ 에이전트 간 작업 파일 (`_workspace/`) — 마크다운 유지
- ❌ Plan 도구 / 단순 의사결정 안건 — 채팅 마크다운

## 갱신 정책

- 마크다운 소스가 갱신되면 HTML도 함께 갱신
- 새 학습 자료는 `reports/learning/NN_topic.html` 순번대로
- base.css 변경 시 모든 HTML이 자동 반영

## 품질 체크리스트

각 HTML 생성 후 확인:
- [ ] `<html lang="ko">` 명시
- [ ] base.css 참조 경로 정확 (`../_assets/base.css`)
- [ ] KaTeX 스크립트 포함 (수식 있으면)
- [ ] `<header class="doc-header">`로 시작
- [ ] `<footer class="doc-footer">`로 출처·생성일 명시
- [ ] 표는 `<table>`, 코드는 `<pre><code>`, 콜아웃은 `.callout`
- [ ] 모든 단계 절차는 `<ol class="steps">` (있는 경우)
