import streamlit as st
import pandas as pd

from data_loader import load_music_data
from recommender import (
    TYPE_DESCRIPTIONS,
    make_neutral_profile,
    classify_music_type,
    build_profile_by_type,
    adjust_profile_by_sliders,
    recommend_track,
)
from profile_store import load_user_profile, save_user_profile


USER_ACCOUNTS = {
    "student01": "M7qP9xL2",
    "musiclab": "T4vR8nK6",
    "demo_user": "A9sD3fG7",
    "tester": "Q2wE6rT8",
}


st.set_page_config(
    page_title="CrowTune 음악 추천 앱",
    layout="centered",
)


# =========================
# 함수 정의
# =========================

def reset_session():
    st.session_state.profile = make_neutral_profile()
    st.session_state.music_type = ""
    st.session_state.quiz_done = False
    st.session_state.current_track = None
    st.session_state.seen_track_ids = []
    st.session_state.recommend_count = 0


def make_save_data():
    return {
        "profile": st.session_state.profile,
        "music_type": st.session_state.music_type,
        "quiz_done": st.session_state.quiz_done,
        "seen_track_ids": st.session_state.seen_track_ids,
        "recommend_count": st.session_state.recommend_count,
    }


def save_current_user_state():
    if st.session_state.login:
        save_user_profile(st.session_state.username, make_save_data())


def restore_user_state(saved_data):
    st.session_state.profile = saved_data.get("profile", make_neutral_profile())
    st.session_state.music_type = saved_data.get("music_type", "")
    st.session_state.quiz_done = saved_data.get("quiz_done", False)
    st.session_state.seen_track_ids = saved_data.get("seen_track_ids", [])
    st.session_state.recommend_count = saved_data.get("recommend_count", 0)
    st.session_state.current_track = None


def show_profile_chart(profile):
    chart_data = pd.DataFrame({
        "특성": [
            "리듬감",
            "에너지",
            "음량감",
            "포엠/랩",
            "어쿠스틱",
            "연주 중심",
            "라이브감",
            "밝은 분위기",
            "속도",
        ],
        "현재 내 취향값": [
            profile["danceability"],
            profile["energy"],
            profile["loudness_norm"],
            profile["speechiness"],
            profile["acousticness"],
            profile["instrumentalness"],
            profile["liveness"],
            profile["valence"],
            profile["tempo_norm"],
        ],
    })

    chart_data = chart_data.set_index("특성")

    st.subheader("내 음악 취향")
    st.write(
        "유형 판별 퀴즈와 5단계 평가를 통해 누적된 취향 현황을 막대그래프로 보여줍니다."
    )

    st.bar_chart(chart_data)

    with st.expander("수치 데이터 보기"):
        st.dataframe(chart_data)


# =========================
# 세션 상태 초기화
# =========================

if "login" not in st.session_state:
    st.session_state.login = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "profile" not in st.session_state:
    st.session_state.profile = make_neutral_profile()

if "music_type" not in st.session_state:
    st.session_state.music_type = ""

if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = False

if "current_track" not in st.session_state:
    st.session_state.current_track = None

if "seen_track_ids" not in st.session_state:
    st.session_state.seen_track_ids = []

if "recommend_count" not in st.session_state:
    st.session_state.recommend_count = 0


# =========================
# 상단 제목 + 캐시 초기화
# =========================

title_col, button_col = st.columns([4, 1])

with title_col:
    st.title("CrowTune")
    st.subheader("노래 취향 유형 판별 및 피드백을 통한 알고리즘 최적화")

with button_col:
    st.write("")
    st.write("")
    if st.button("캐시 초기화"):
        st.cache_data.clear()
        st.success("캐시가 초기화되었습니다.")
        st.rerun()


st.info("""
학생 정보

- 학번: 2022204057
- 이름: 배지원
""")

st.write(
    "이 앱은 노래 취향 유형 판별 검사를 먼저 진행한 뒤, "
    "추천곡에 대한 5단계 피드백을 반영하여 반복적으로 새로운 곡을 추천합니다."
)

if st.session_state.login:
    st.success(
        st.session_state.username
        + "님은 로그인 상태입니다. 추천 결과가 자동 저장됩니다."
    )
else:
    st.warning(
        "현재 비로그인 상태입니다. 앱 이용은 가능하지만 새로 접속하면 결과가 초기화됩니다."
    )


# =========================
# 탭 구성
# =========================

tab1, tab2, tab3 = st.tabs(
    ["로그인", "유형 판별 퀴즈", "추천과 5단계 평가"]
)


# =========================
# 로그인 탭
# =========================

with tab1:
    st.header("로그인")

    st.write(
        "로그인하지 않아도 앱을 이용할 수 있습니다. "
        "다만 로그인하지 않으면 접속이 초기화될 때 결과가 유지되지 않습니다."
    )

    st.write(
        "로그인하면 이전에 저장된 노래 취향 유형과 누적 취향값을 불러와 "
        "추천에 다시 반영합니다."
    )

    if st.session_state.login is False:
        user_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")

        if st.button("로그인"):
            if user_id in USER_ACCOUNTS and password == USER_ACCOUNTS[user_id]:
                st.session_state.login = True
                st.session_state.username = user_id

                saved_data = load_user_profile(user_id)

                if saved_data:
                    restore_user_state(saved_data)
                    st.success("로그인 성공: 저장된 취향 결과를 불러왔습니다.")
                else:
                    reset_session()
                    st.success("로그인 성공: 새 취향 분석을 시작합니다.")

                st.rerun()

            else:
                st.error("로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다.")

        st.caption("테스트용 아이디: student01 / 비밀번호: M7qP9xL2")

    else:
        st.success(st.session_state.username + "님, 로그인 상태입니다.")

        if st.button("현재 취향 결과 저장"):
            save_current_user_state()
            st.success("현재 취향 결과가 저장되었습니다.")

        if st.button("로그아웃"):
            st.session_state.login = False
            st.session_state.username = ""
            reset_session()
            st.success("로그아웃되었습니다.")
            st.rerun()


# =========================
# 유형 판별 퀴즈 탭
# =========================

with tab2:
    st.header("노래 취향 유형 판별 퀴즈")

    st.write(
        "먼저 간단한 유형 판별형 퀴즈를 통해 사용자의 주된 취향을 정합니다. "
        "이 결과가 첫 추천곡의 기준이 됩니다."
    )

    q1 = st.radio(
        "1. 노래를 들을 때 가장 먼저 끌리는 요소는?",
        [
            "강한 에너지와 몰입감",
            "감정선과 분위기",
            "리듬과 그루브",
            "잔잔하고 편안한 사운드",
        ],
    )

    q2 = st.radio(
        "2. 지금 가장 듣고 싶은 상황은?",
        [
            "운동하거나 텐션을 올리고 싶을 때",
            "혼자 생각에 잠기고 싶을 때",
            "걸으면서 리듬을 타고 싶을 때",
            "공부하거나 쉬면서 편하게 듣고 싶을 때",
        ],
    )

    q3 = st.radio(
        "3. 선호하는 곡의 분위기는?",
        [
            "강렬하고 선명한 분위기",
            "어둡거나 감성적인 분위기",
            "움직임이 느껴지는 분위기",
            "부드럽고 자연스러운 분위기",
        ],
    )

    q4 = st.radio(
        "4. 다음 중 더 마음에 드는 표현은?",
        [
            "폭발적인 후렴",
            "서정적인 감정",
            "중독적인 비트",
            "따뜻한 음색",
        ],
    )

    if st.button("내 노래 취향 유형 확인하고 추천 시작"):
        scores = {
            "에너지 부스터형": 0,
            "감성 몰입형": 0,
            "리듬 탐색형": 0,
            "어쿠스틱 힐링형": 0,
        }

        answer_map = {
            q1: {
                "강한 에너지와 몰입감": "에너지 부스터형",
                "감정선과 분위기": "감성 몰입형",
                "리듬과 그루브": "리듬 탐색형",
                "잔잔하고 편안한 사운드": "어쿠스틱 힐링형",
            },
            q2: {
                "운동하거나 텐션을 올리고 싶을 때": "에너지 부스터형",
                "혼자 생각에 잠기고 싶을 때": "감성 몰입형",
                "걸으면서 리듬을 타고 싶을 때": "리듬 탐색형",
                "공부하거나 쉬면서 편하게 듣고 싶을 때": "어쿠스틱 힐링형",
            },
            q3: {
                "강렬하고 선명한 분위기": "에너지 부스터형",
                "어둡거나 감성적인 분위기": "감성 몰입형",
                "움직임이 느껴지는 분위기": "리듬 탐색형",
                "부드럽고 자연스러운 분위기": "어쿠스틱 힐링형",
            },
            q4: {
                "폭발적인 후렴": "에너지 부스터형",
                "서정적인 감정": "감성 몰입형",
                "중독적인 비트": "리듬 탐색형",
                "따뜻한 음색": "어쿠스틱 힐링형",
            },
        }

        for answer, type_dict in answer_map.items():
            selected_type = type_dict[answer]
            scores[selected_type] += 1

        result_type = classify_music_type(scores)
        profile = build_profile_by_type(result_type)

        df = load_music_data()
        track = recommend_track(df, profile, [])

        st.session_state.music_type = result_type
        st.session_state.profile = profile
        st.session_state.current_track = track.to_dict()
        st.session_state.seen_track_ids = [track["track_id"]]
        st.session_state.recommend_count = 1
        st.session_state.quiz_done = True

        save_current_user_state()

        st.success("유형 판별이 완료되었습니다.")
        st.write("당신의 노래 취향 유형:", result_type)
        st.write(TYPE_DESCRIPTIONS[result_type])
        st.info("추천과 5단계 평가 탭에서 첫 추천곡을 확인하세요.")


# =========================
# 추천과 5단계 평가 탭
# =========================

with tab3:
    st.header("추천과 5단계 평가")

    if st.session_state.quiz_done is False:
        st.info("먼저 유형 판별 퀴즈를 완료해주세요.")

    else:
        track = st.session_state.current_track

        if track is None:
            df = load_music_data()
            new_track = recommend_track(
                df,
                st.session_state.profile,
                st.session_state.seen_track_ids,
            )
            track = new_track.to_dict()
            st.session_state.current_track = track

        st.subheader("현재 추천곡")
        st.write("현재 유형:", st.session_state.music_type)
        st.write("추천 횟수:", st.session_state.recommend_count)

        st.markdown(f"### {track['track_name']}")
        st.write("아티스트:", track["artists"])
        st.write("앨범:", track["album_name"])
        st.write("장르:", track["track_genre"])
        st.write("인기도:", int(track["popularity"]))

        spotify_url = "https://open.spotify.com/track/" + track["track_id"]
        st.markdown(f"[Spotify에서 열기]({spotify_url})")

        st.write("---")
        st.subheader("곡의 주요 특성")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("Danceability:", round(track["danceability"], 3))
            st.write("Energy:", round(track["energy"], 3))
            st.write("Valence:", round(track["valence"], 3))

        with col2:
            st.write("Acousticness:", round(track["acousticness"], 3))
            st.write("Speechiness:", round(track["speechiness"], 3))
            st.write("Instrumentalness:", round(track["instrumentalness"], 3))

        with col3:
            st.write("Liveness:", round(track["liveness"], 3))
            st.write("Tempo:", round(track["tempo"], 1))
            st.write("Loudness:", round(track["loudness"], 2))

        st.write("---")
        show_profile_chart(st.session_state.profile)

        st.write("---")
        st.subheader("5단계 취향 평가")

        st.write(
            "현재 추천곡을 듣고 다음 추천곡이 어떤 방향이면 좋을지 평가하세요. "
            "각 값은 사용자의 취향 프로필에 누적 반영됩니다."
        )

        mood_level = st.slider(
            "분위기: 더 차분하고 어두운 분위기 ↔ 더 밝고 신나는 분위기",
            min_value=-2,
            max_value=2,
            value=0,
        )

        energy_level = st.slider(
            "에너지: 더 잔잔한 곡 ↔ 더 강렬한 곡",
            min_value=-2,
            max_value=2,
            value=0,
        )

        tempo_level = st.slider(
            "속도: 더 느린 곡 ↔ 더 빠른 곡",
            min_value=-2,
            max_value=2,
            value=0,
        )

        rhythm_level = st.slider(
            "리듬감: 리듬감이 약한 곡 ↔ 리듬감이 강한 곡",
            min_value=-2,
            max_value=2,
            value=0,
        )

        acoustic_level = st.slider(
            "사운드 질감: 더 전자적인 사운드 ↔ 더 어쿠스틱한 사운드",
            min_value=-2,
            max_value=2,
            value=0,
        )

        if st.button("평가 반영해서 새 노래 추천"):
            df = load_music_data()

            new_profile = adjust_profile_by_sliders(
                st.session_state.profile,
                mood_level,
                energy_level,
                tempo_level,
                rhythm_level,
                acoustic_level,
            )

            new_track = recommend_track(
                df,
                new_profile,
                st.session_state.seen_track_ids,
            )

            st.session_state.profile = new_profile
            st.session_state.current_track = new_track.to_dict()
            st.session_state.seen_track_ids.append(new_track["track_id"])
            st.session_state.recommend_count += 1

            save_current_user_state()

            st.success("평가가 반영되었습니다. 새로운 추천곡을 불러옵니다.")
            st.rerun()

        with st.expander("현재 누적 취향값 보기"):
            st.write(st.session_state.profile)