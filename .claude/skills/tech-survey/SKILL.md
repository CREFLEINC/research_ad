---
name: tech-survey
description: "Anomaly Detection 기술 조사를 체계적으로 수행하는 절차. tech-surveyor 에이전트가 사용. 분류 체계 → SOTA 수치 → 오픈소스 매트릭스 → 산업 사례 → 참고 자료 순서로 구조화된 보고서 산출. 'AD 기술 조사', '이상 탐지 최신 기법', '벤치마크 정리' 요청 시 사용."
---

# Tech Survey — Anomaly Detection 기술 조사 절차

`tech-surveyor` 에이전트가 사용하는 절차적 스킬. 목적은 **객관적이고 재현 가능한 기술 지도** 작성.

## 1. 분류 체계 매핑

다음 카테고리를 빠짐없이 다룬다 (해당 영역이 비어도 "해당 없음" 명시):

| 카테고리 | 대표 기법 |
|---------|----------|
| Reconstruction-based | AutoEncoder, VAE, MemAE, RIAD |
| Embedding/Memory-bank | PaDiM, PatchCore, SPADE |
| Normalizing Flow | FastFlow, CFLOW-AD, CS-Flow |
| Knowledge Distillation | STFPM, EfficientAD, ReContrast |
| Synthesis-based | DRAEM, CutPaste, NSA |
| Diffusion-based | AnomalyDiffusion, DDAD |
| One-class Classification | DeepSVDD, PANDA |
| Vision-Language | WinCLIP, AnomalyCLIP, AprilGAN |

각 카테고리당 1~3개의 대표 기법을 수치와 함께 정리.

## 2. SOTA 성능 비교표

표준 형식 (각 데이터셋별로 표 1개):

```
### MVTec AD
| 모델 | 발표년도 | Image AUROC | Pixel AUROC | AUPRO | 재현성 | 라이선스 |
|------|---------|-------------|-------------|-------|--------|----------|
| ... |
```

- 수치는 **공식 논문 보고치 + 가능하면 anomalib 등 독립 재현치** 병기
- 재현성 라벨: ★(검증됨) / ☆(미검증) / ✗(재현 실패 보고)

## 3. 오픈소스 매트릭스

```
| 라이브러리/저장소 | 포함 모델 | 라이선스 | 최근 업데이트 | Star/Fork | 비고 |
|------------------|-----------|----------|--------------|-----------|------|
| openvinotoolkit/anomalib | PatchCore, PaDiM, FastFlow, EfficientAD ... | Apache 2.0 | YYYY-MM | | 사실상 표준 |
| ...
```

**중복 구현 방지 원칙**: 보고서에 "이 라이브러리가 있으면 직접 구현 불필요" 라벨링.

## 4. 산업 적용 사례 및 한계 보고

- 발표된 산업 사용 사례 (논문/블로그/케이스 스터디)
- 보고된 실패 사례 또는 한계
- 산업 KPI (latency, FPS, FPR 등)와의 격차

## 5. 참고 자료

모든 인용에 URL 또는 DOI 첨부. 가능하면 발표 연도 표기.

## 도구 활용

- **WebSearch**: 최신 논문, 벤치마크 사이트, GitHub 동향
- **WebFetch**: 특정 페이지 상세 확인
- **context7 MCP**: anomalib, PyTorch, torchvision 등 라이브러리 공식 문서

## 출력 위치

`_workspace/01_survey/survey_report.md` (단일 파일)

추가 자료(논문 PDF 인용 발췌 등)는 `_workspace/01_survey/references/`에 보관.

## 품질 기준

- 모든 수치에 출처 명시
- 추정값 작성 금지 — 모르는 칸은 빈칸 + "수치 불명"
- 보고서 분량은 본문 200~400줄 (참조 자료 별도)
