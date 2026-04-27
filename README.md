# CrowTune

Streamlit 중간고사 대체 과제로 만든 음악 추천 앱입니다.

## 프로젝트 소개

이 앱은 사용자의 노래 취향을 유형별로 판별한 뒤, 추천곡에 대한 5단계 평가를 반영해서 계속 새로운 노래를 추천합니다.

처음에는 간단한 유형 판별 퀴즈를 진행하고, 이후 사용자가 추천곡에 대해 평가하면 그 결과가 취향값에 반영됩니다.

## 제출자 정보

- 학번: 2022204057
- 이름: 배지원

## 주요 기능

- 로그인 기능
- 비로그인 상태에서도 앱 이용 가능
- 노래 취향 유형 판별 퀴즈
- 음악 데이터 기반 추천
- 5단계 평가를 통한 반복 추천
- Streamlit 캐싱 기능 사용

## 로그인 정보

테스트용 계정은 아래와 같습니다.

- 아이디: student01
- 비밀번호: M7qP9xL2

## 파일 구성

app.py              # Streamlit 메인 실행 파일
data_loader.py      # 음악 데이터 불러오기 및 전처리
recommender.py      # 취향 유형 판별 및 추천 알고리즘
music_data.csv.gz   # 압축된 음악 데이터
requirements.txt    # 실행에 필요한 라이브러리
.gitignore          # GitHub에 올리지 않을 파일 설정
README.md           # 프로젝트 설명

## 사용한 자료 출처

Spotify Tracks Dataset: https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset?resource=download
