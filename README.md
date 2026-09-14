# Cozy City / 로우폴리 도시·마을 생성기

Blender에서 실행하는 **300×300m 도시 / 180×180m 마을 생성기**입니다.
[octopus7/astra-blender-forest](https://github.com/octopus7/astra-blender-forest)의
**저폴리 메시 조립 + 버텍스 컬러 + 공유 메시 + 재현 가능한 배치** 방식을 도시 제작에 응용했습니다.
숲을 건물로 무작위 치환한 것이 아니라 **도로 → 블록 → 필지 → 건물 → 소품** 순으로 배치합니다.

> 검증 상태: Python 자동 테스트 21개 통과. 도시·마을 GLB 생성 및 독립 라이브러리 재읽기 확인.
> Chromium의 CPU 미리보기에서 실제 메시 표시와 카메라 버튼 확인.
> **Blender 4.2+ API를 대상으로 작성했지만 Blender 앱, GPU WebGL, Godot/Unreal 실행은 미검증입니다.**
> 해당 범위를 통과한 것으로 표시하지 않습니다. [검증 보고서](docs/TEST_REPORT.md)

## 1. Blender에서 시작하기

1. GitHub의 **Code → Download ZIP**으로 내려받고, **압축을 전부 해제**합니다.
2. Blender **Scripting → Text Editor → Open**에서 `01_build_city.py`를 엽니다.
3. 텍스트 편집기에 마우스를 놓고 **Alt+P / Run Script**를 실행합니다.
4. 새로 생성된 `CC_CozyCity` 씬을 확인하고 `.blend`를 직접 저장합니다.
5. 3D 화면에서 **N → Cozy City** 패널을 열면 도시/마을, 배치 번호, 나무, 차량을 변경할 수 있습니다.

기존 작업 씬은 지우지 않습니다. 다만 **재생성하면 이전 `CC_CozyCity` 씬의 수동 편집은 교체됩니다.**
편집을 보존하려면 별도 `.blend`로 저장한 뒤 재생성하세요.
패널은 스크립트를 실행한 현재 Blender 세션에 등록됩니다. 영구 설치형 애드온은 아닙니다.
새 세션에서 저장한 장면만 열어도 모델은 남지만 패널은 자동 등록되지 않습니다.

## 2. Blender 없이 결과 확인하기

Python 3.10 이상, **추가 패키지 설치 없이** 실행합니다.

```bash
python build_city.py --preset city --seed 42 --out output/city
python build_city.py --preset village --seed 42 --out output/village
```

생성 폴더의 `preview.html`을 브라우저에서 엽니다. 인터넷, CDN, 외부 폰트가 필요 없습니다.
드래그로 회전, 휠로 확대/축소하고 전체/평면/중앙 광장 버튼을 사용할 수 있습니다.
GPU WebGL 사용이 불가능하면 CPU 방식으로 실제 메시를 그립니다.
CPU 방식은 느릴 수 있으며 미리보기에는 그림자·반사·최종 렌더 효과가 없습니다.

| 생성 파일 | 용도 |
|---|---|
| `city.glb` | 도시 전체 3D 모델. 마을도 같은 파일명으로 생성됩니다. |
| `manifest.json` | 공유 모델 정보, 위치, 회전, 축척, 필지 경계, 통계 |
| `preview.html` | 모델 데이터를 내장한 오프라인 3D 미리보기 |

같은 폴더의 생성물을 덮어쓰려면 명시적으로 `--force`를 붙입니다.

## 3. 포함되는 모델과 배치

| 항목 | 구현 내용 |
|---|---|
| 건축 | 2층 주택, 2층 상점, 4층 공동주택, 시계탑 시청 |
| 건물 표현 | 지붕·굴뚝·창틀·문·계단·띠 장식·차양·간판판·화단 |
| 도로 | 연결된 격자 도로, 교차로, 중앙선, 횡단보도, 보도 영역 |
| 공공 공간 | 중앙 광장, 분수, 연못 공원, 벤치, 가로등 |
| 환경 | 4종 가로수, 4색 차량, 잔디 마당 |
| 반복 생성 | 같은 seed(배치 번호)로 같은 결과, 다른 번호로 색·종류·차량 배치 변경 |
| 재사용 | 같은 모델은 Blender Mesh 데이터를 공유. 전체를 하나의 메시로 합치지 않음 |

간판은 색상 판 형태이며 상호 텍스트나 상표를 넣지 않았습니다.
주택·상점·공동주택은 각각 4색 계열을 사용합니다. 공통 형태의 색상 변형이며 12가지 완전히 다른 건축 양식은 아닙니다.
시청은 도서관형 건물 레시피에 시계탑을 조합한 원본 도시 에셋입니다.

### 기본 seed 42 기준 실제 생성 수치

| 항목 | 도시 | 마을 |
|---|---:|---:|
| 지도 | 300×300m | 180×180m |
| 건물 | 93 | 29 |
| 배치 오브젝트 | 512 | 196 |
| 재사용 메시 | 32 | 27 |
| 고유 메시 삼각형 합계 | 24,052 | 13,820 |
| 배치 후 삼각형 합계 | 196,966 | 57,366 |

공유 메시를 사용해도 화면에 그리는 전체 삼각형과 드로콜이 사라지는 것은 아닙니다.
모바일/VR 성능 보장은 아니며, 타깃 기기에서 별도 최적화가 필요합니다.

## 4. 크기와 배치 변경

`city_config.json`의 `preset`을 `village`로 바꾸면 마을을 생성합니다.

```json
{
  "preset": "city",
  "seed": 42,
  "trees": true,
  "cars": true
}
```

세부 설정은 `blocks`(3/5/7), `block_size`(38~60m), `road_width`(7~16m), `margin`(5~40m)입니다.
지도 크기는 이 값으로 자동 계산됩니다. `map_size`를 직접 입력하지 않습니다.
좁은 블록에서는 건물 전체를 균일 축소해 보도 영역을 확보합니다.
UI의 생성 버튼은 선택한 **기본 프리셋**을 사용합니다. 사용자 지정 크기는 JSON을 바꾸고 `01_build_city.py`를 재실행하세요.
일반 Python에서 JSON을 적용하려면 `python build_city.py --config city_config.json --out output/custom`을 실행합니다.

## 5. 편집한 Blender 장면 내보내기

`CC_CozyCity` 씬에서 Object Mode로 전환하고, 생성 컬렉션과 오브젝트를 모두 보이게 합니다.
`02_export_city.py`를 실행하거나 **N → Cozy City → GLB 내보내기**를 누릅니다.
`output/edited_city.glb`와 `output/edited_city.placements.json`이 생성됩니다.
이 작업은 같은 이름의 기존 내보내기 파일을 덮어씁니다.

**실제 편집된 장면**을 내보내므로 이동·회전·크기 변경이 반영됩니다.
자동 생성 태그가 있는 메시만 포함되며, 카메라와 조명은 제외합니다.
새로 만든 사용자 오브젝트는 자동 포함하지 않습니다. 생성 모델을 복제한 오브젝트는 태그가 유지됩니다.
반면 `build_city.py`는 seed에서 다시 만드는 도구이므로 Blender의 수동 편집을 읽지 않습니다.

GLB는 Y-up, 배치 JSON은 Blender와 같은 **미터 / Z-up** 기준입니다.
원본 숲 저장소의 Unreal 전용 FBX/HISM 자동 임포터는 이번 버전에 포함하지 않았습니다.
Godot/Unreal의 임포트·물리·최적화 설정까지 완료된 게임 레벨은 아닙니다.

## 6. 구조와 후속 개발

```text
01_build_city.py          Blender 장면 생성 시작점
02_export_city.py         편집한 Blender 장면 내보내기
build_city.py             일반 Python 생성·GLB·미리보기
city_config.json          기본 설정
cozy_city/mesh.py         저폴리 도형 조립
cozy_city/assets.py       건물·가로수·도로·소품
cozy_city/layout.py       도시 계획·배치·검사
cozy_city/export.py       GLB·배치표 출력
cozy_city/blender_scene.py Blender 연동·N 패널
cozy_city/viewer.html     독립 실행 미리보기 템플릿
tests/test_city.py        자동 테스트
```

코덱스 후속 작업은 [AGENTS.md](AGENTS.md)를 먼저 읽으세요.
현재 미포함: 건물 내부, 충돌체, 네비게이션, LOD, 지형 고저차, 곡선 도로, 실제 상호,
교통 시뮬레이션, 한국/베트남 특화 건축, 영구 설치형 애드온.

```bash
python -m unittest discover -s tests -v
```

## 출처 / 라이선스

MIT. 도형 조립 헬퍼와 나무 표현 방식은 원본의 허용 조건에 따라 응용했고,
도시 계획·건축·GLB·UI·미리보기는 이 저장소용으로 작성했습니다.
[LICENSE](LICENSE)와 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)를 보존하세요.
