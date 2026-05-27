# Anomaly Detection — 제조 머신 비전 연구

딥러닝 기반 Anomaly Detection 기술을 연구 단계에서 실제 제조 생산 현장에서 활용 가능한 **제품화 수준**으로 끌어올리기 위한 연구 프로젝트.

## 📖 Live HTML Reports

**🔗 Pages URL:** https://crefleinc.github.io/research_ad/

- **학습 자료 (모델별 심화 해설)**
  - [① PatchCore](https://crefleinc.github.io/research_ad/reports/learning/01_patchcore.html) — Embedding / Memory-bank (CVPR 2022)
  - [② EfficientAD](https://crefleinc.github.io/research_ad/reports/learning/02_efficient_ad.html) — Knowledge Distillation + Autoencoder (WACV 2024)
  - *(추가 예정)* ③ MuSc · ④ AnomalyCLIP · ⑤ Dinomaly

## 🎯 연구 목표

| Top-3 한계 | 분류 |
|-----------|------|
| 산업 KPI(recall@FPR=0.1%) 공개 보고 부재 | Blocker |
| 도메인 시프트 — MVTec AD 2 / Real-IAD에서 SOTA 급락 | Blocker |
| 미세결함 × latency Pareto frontier 미정량 | Mitigable |

## 🧪 채택안 (Phase 3 합의)

| ID | 안 | 핵심 |
|----|----|----|
| **P1** | IF-PROTO | recall@FPR={0.1%, 0.5%, 1%} + bootstrap CI + per-defect-size + Pareto frontier 표준화 |
| **P2** | CS-BRIDGE | MuSc + AnomalyCLIP zero-shot agreement → pseudo-label → PatchCore 학습 (cold-start 14일) |

## 🛠 코드 구조

```
code/
├── README.md
├── requirements.txt
├── configs/        # P1, P2 실험 설정
├── src/
│   ├── metrics/    # recall@FPR + bootstrap CI, per-size, Pareto, ECE
│   ├── calibration/  # Platt / Isotonic
│   ├── coldstart/  # MuSc pseudo-label, error correlation
│   ├── data/
│   ├── models/
│   ├── train.py
│   └── evaluate.py
├── scripts/        # 다운로드, demo 실행
└── tests/          # 메트릭 검증 unit test
```

## 🏗 연구 하네스

본 프로젝트는 6 에이전트 + 6 스킬의 [Claude Code 하네스](.claude/)로 운영:

- **tech-surveyor** — 기술 조사
- **tech-validator** — 검증 + 한계 도출
- **researcher-novelty / pragmatist / critic** — 3인 연구팀 (창의·실용·비판)
- **developer** — 구현·검증

각 Phase에 사용자 의사결정 게이트 — 모든 연구 산출물에 수치 객관성 + 확률 근거 의무.

## 🤝 활용 오픈소스

- [anomalib](https://github.com/openvinotoolkit/anomalib) (Apache 2.0) — 베이스라인 5종 (PatchCore, EfficientAD, ...)
- [MuSc](https://github.com/xrli-U/MuSc) (MIT) — zero-shot
- [AnomalyCLIP](https://github.com/zqhang/AnomalyCLIP) (MIT)
- [Dinomaly](https://github.com/guojiajeremy/Dinomaly) (MIT)
- [GLASS](https://github.com/cqylunlun/GLASS) (MIT)

## 📜 라이선스

연구 코드: MIT (별도 명시 시) · 데이터셋(MVTec AD, VisA, Real-IAD)은 각 제공자 약관 준수.

---

*본 저장소는 진행 중인 연구의 가독본을 호스팅합니다. 내부 연구 노트(`_workspace/`)는 공개되지 않습니다.*
