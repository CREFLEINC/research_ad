---
name: implementation-and-verification
description: "연구팀이 합의한 Anomaly Detection 방안을 코드로 구현하고 정량 검증하는 절차. developer 에이전트가 사용. 오픈소스 우선 활용, 표준 벤치마크에서 베이스라인 대비 측정, 재현 가능한 환경 산출. '아이디어 구현', '학습 코드 작성', '검증 실험', '결과 리포트' 요청 시 사용."
---

# Implementation and Verification — 구현·검증 절차

`developer` 에이전트가 사용. 합의된 연구안을 작동하는 코드로 만들고 정량 검증한다.

## 1. 구현 전 사전 점검

코드 작성 전 다음을 확인:

1. **오픈소스 활용 가능성** — 합의안에 포함된 활용 가능 자원 (anomalib, timm 등)을 실제로 검증:
   - 저장소 최신 commit 날짜
   - 의존성 호환성 (PyTorch 버전, CUDA 등)
   - Issues에서 보고된 알려진 문제
   - `context7` MCP로 공식 문서 확인
2. **데이터셋 접근성** — MVTec AD, VisA, BTAD 등 다운로드 경로 확보
3. **연산 자원** — 학습 시간 추정, GPU 메모리 요구치

→ 점검 결과를 `_workspace/04_implementation/pre_check.md`에 기록

## 2. 프로젝트 구조

```
code/
├── README.md
├── requirements.txt (또는 environment.yml)
├── configs/
│   └── {experiment_name}.yaml
├── src/
│   ├── data/           # 데이터 로더 (가능하면 anomalib 사용)
│   ├── models/         # 새로 구현한 핵심 모듈만
│   ├── train.py
│   ├── evaluate.py
│   └── utils/
├── scripts/
│   └── download_data.sh
└── results/            # 학습 결과 저장 (.gitignore)
```

**중복 구현 금지 원칙:** 데이터 로더, 표준 모델, 평가 메트릭은 가능한 한 라이브러리 호출.

## 3. 검증 설계

### 측정 지표 (최소 셋)
- Image-level AUROC
- Pixel-level AUROC
- AUPRO
- recall @ FPR=0.1%
- 추론 latency (ms/image) on {GPU/CPU}
- 모델 크기 (params, MB)

### 베이스라인 비교
선택된 베이스라인 (최소 1개) — 일반적으로 anomalib의 PatchCore 또는 EfficientAD.
동일 데이터셋, 동일 split, 동일 시드로 두 결과를 함께 보고.

### 시드 및 환경
- random seed 3개로 실험 (예: 42, 1337, 2024)
- 결과는 평균 ± 표준편차로 보고
- Python/PyTorch 버전, GPU 모델, CUDA 버전 명시

## 4. 결과 리포트

`_workspace/04_implementation/results.md`:

```
# 구현 및 검증 결과

## 1. 구현 개요
- 사용한 오픈소스: <라이브러리 목록>
- 추가 구현 모듈: <목록>
- 합의안 ID: <consolidated_proposals.md의 어떤 안>

## 2. 환경
- HW: GPU/RAM/CPU
- SW: Python/PyTorch/anomalib 버전
- Seed: [42, 1337, 2024]

## 3. 데이터셋
- {데이터셋명}, {카테고리}, train/test split

## 4. 실험 결과 (수치 표)
| 모델 | Image AUROC | Pixel AUROC | AUPRO | recall@FPR=0.1% | latency(ms) | params |
| 베이스라인(PatchCore) | ... |
| 제안 방법 | ... |

## 5. 베이스라인 대비 비교
- 절대 개선치와 상대 개선치 모두 표기
- 통계적 유의성 (시드별 분산 대비)

## 6. 결과 해석
- 가설 검증 결과 (어떤 가정이 검증되었고 어떤 가정이 깨졌는가)
- 예상과 다른 결과 (있다면)

## 7. 한계 및 다음 단계

## 8. 재현 명령어
```bash
$ git clone ...
$ pip install -r requirements.txt
$ bash scripts/download_data.sh
$ python src/train.py --config configs/...
$ python src/evaluate.py --checkpoint ...
```
```

## 5. 실패 보고 원칙

학습이 실패하거나 수치가 가설에 못 미치면:
- **수정/조작 금지**: 결과를 그대로 보고
- 실패 분석 섹션 추가 — 어떤 가정이 깨졌는가
- 가능하면 ablation으로 어디서 차이가 났는지 분석
- 연구팀의 `researcher-critic`에게 `SendMessage`로 가정 재검토 요청 가능

## 6. 후속 실행 처리

이전 결과가 존재하면:
- 새 안을 추가 검증할 때는 새 실험명으로 분리
- 동일 안의 개선 검증이면 이전 결과를 baseline 행에 포함 (regression 추적)

## 출력 위치

```
code/                              # 실제 구현 (커밋 가능)
_workspace/04_implementation/
├── pre_check.md
├── results.md
└── logs/                          # 학습 로그 (TensorBoard 등)
```

## 도구 활용

- `context7` MCP: anomalib, PyTorch Lightning 등 최신 API
- Bash: 학습 실행, GPU 모니터링
- Read/Edit/Write: 코드 작성
