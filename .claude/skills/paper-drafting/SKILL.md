---
name: paper-drafting
description: "연구 과정과 구현 결과를 5페이지 이내 논문 형식으로 정리하는 절차. 모든 연구 산출물(조사·검증·합의·구현)을 인용 기반으로 통합. '논문 작성', '논문 초안', '5페이지 논문', '연구 결과 정리' 요청 시 사용."
---

# Paper Drafting — 5페이지 이내 논문 초안 작성 절차

전체 연구 산출물을 5페이지 이내 짧은 논문(워크숍/short paper 형식)으로 정리한다.

## 1. 입력 자료 매핑

| 논문 섹션 | 입력 자료 |
|----------|----------|
| Abstract | 전체 산출물 요약 |
| 1. Introduction | `validation_report.md`의 Top-3 한계 |
| 2. Related Work | `survey_report.md`의 분류 체계 + SOTA |
| 3. Method | `consolidated_proposals.md`의 채택안 + `code/` |
| 4. Experiments | `results.md` |
| 5. Discussion & Conclusion | `residual_risks.md` + 결과 해석 |

## 2. 페이지 배분 (총 5페이지)

- Abstract + Introduction: 0.75p
- Related Work: 0.75p
- Method: 1.5p
- Experiments: 1.5p
- Discussion & Conclusion + References: 0.5p

> 그림/표 포함. 그림은 2~3개, 표는 1~2개.

## 3. 구조 (IEEE 또는 CVPR 단순 양식)

```
# Title (제목)
Authors

## Abstract (150~200 words)
- 문제 정의 (산업 AD의 한계)
- 본 연구의 기여 (구체적 1~3개)
- 핵심 결과 수치

## 1. Introduction
- 제조 머신 비전 AD의 중요성과 한계
- 본 연구가 다루는 한계 (Top-3 중 채택안)
- 기여 bullet (3개 이내)

## 2. Related Work
- AD 분류 체계 압축본
- 채택 방안과 직접 관련된 선행 연구 위주

## 3. Method
- 합의된 핵심 메커니즘 (수식 + 그림 1개)
- 오픈소스 기반 부분 vs. 신규 부분 명시

## 4. Experiments
- 4.1 Setup: 데이터셋, 베이스라인, 지표
- 4.2 Main Results: 비교 표
- 4.3 Ablation (있다면)
- 4.4 한계 / 실패 분석 (정직하게)

## 5. Discussion & Conclusion
- 결과의 의미
- 잔존 리스크와 향후 작업

## References
- IEEE 형식, 핵심 인용 위주 (20개 이내)
```

## 4. 작성 원칙

- **재현 가능 정보 포함**: 코드 저장소 링크, 데이터셋, 시드
- **수치 정직성**: 베이스라인 대비 개선이 통계적으로 유의하지 않으면 그렇게 명시
- **부정 결과도 가치**: 실패한 가정도 "이 결과는 X 가정이 산업 데이터에 적용 안 됨을 시사" 식으로 기여
- **인용 출처**: `survey_report.md`의 references를 우선 활용

## 5. 표/그림 자동 생성

가능하면 `code/` 안에 plot 생성 스크립트 포함 — 재실행 시 figure가 재생성되도록.

## 출력 위치

```
_workspace/05_paper/
├── paper.md           # 본문 (Markdown)
├── paper.tex          # (선택) LaTeX 변환본
├── figures/           # 그림
└── references.bib     # 참고문헌
```

## 사용자 검토 게이트

초안 완성 후 사용자에게:
- "초안 5페이지 분량 확인 부탁드립니다"
- 수정 요청 받기 (제목, 강조점, 누락 인용 등)
- 승인 시 최종본으로 표시

## 후속 실행

기존 paper 산출물이 있으면:
- 새로운 실험 결과 추가 시 Experiments 섹션만 갱신
- 채택안 변경 시 Method 전면 재작성
