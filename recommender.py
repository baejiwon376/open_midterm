FEATURE_COLUMNS = [
    "danceability",
    "energy",
    "loudness_norm",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo_norm",
]


TYPE_DESCRIPTIONS = {
    "에너지 부스터형": "강한 에너지, 빠른 전개, 높은 몰입감을 선호하는 유형입니다.",
    "감성 몰입형": "밝음보다 감정선, 분위기, 서정성을 더 중요하게 느끼는 유형입니다.",
    "리듬 탐색형": "리듬감, 그루브, 몸이 반응하는 흐름을 중시하는 유형입니다.",
    "어쿠스틱 힐링형": "자극적인 사운드보다 잔잔하고 자연스러운 음악을 선호하는 유형입니다.",
}


def clamp(value):
    if value < 0:
        return 0
    if value > 1:
        return 1
    return value


def make_neutral_profile():
    return {
        "danceability": 0.5,
        "energy": 0.5,
        "loudness_norm": 0.5,
        "speechiness": 0.5,
        "acousticness": 0.5,
        "instrumentalness": 0.5,
        "liveness": 0.5,
        "valence": 0.5,
        "tempo_norm": 0.5,
    }


def build_profile_by_type(type_name):
    profile = make_neutral_profile()

    if type_name == "에너지 부스터형":
        profile["energy"] = 0.82
        profile["loudness_norm"] = 0.72
        profile["tempo_norm"] = 0.68
        profile["valence"] = 0.65

    elif type_name == "감성 몰입형":
        profile["valence"] = 0.25
        profile["acousticness"] = 0.68
        profile["energy"] = 0.35
        profile["tempo_norm"] = 0.42

    elif type_name == "리듬 탐색형":
        profile["danceability"] = 0.82
        profile["tempo_norm"] = 0.62
        profile["energy"] = 0.60
        profile["speechiness"] = 0.55

    elif type_name == "어쿠스틱 힐링형":
        profile["acousticness"] = 0.82
        profile["energy"] = 0.25
        profile["loudness_norm"] = 0.35
        profile["valence"] = 0.55

    return profile


def classify_music_type(answer_scores):
    max_score = -1
    result_type = None

    for type_name, score in answer_scores.items():
        if score > max_score:
            max_score = score
            result_type = type_name

    return result_type


def adjust_profile_by_sliders(
    profile,
    mood_level,
    energy_level,
    tempo_level,
    rhythm_level,
    acoustic_level,
):
    """
    각 슬라이더 값은 -2, -1, 0, 1, 2 범위입니다.
    0은 현재 추천 유지, 양수/음수는 특정 방향으로 취향값을 이동시킵니다.
    """
    new_profile = profile.copy()
#1
    new_profile["valence"] = clamp(new_profile["valence"] + mood_level * 0.06)
#2
    new_profile["energy"] = clamp(new_profile["energy"] + energy_level * 0.06)
    new_profile["loudness_norm"] = clamp(new_profile["loudness_norm"] + energy_level * 0.04)
#2
    new_profile["tempo_norm"] = clamp(new_profile["tempo_norm"] + tempo_level * 0.06)
#4
    new_profile["danceability"] = clamp(new_profile["danceability"] + rhythm_level * 0.06)
#5
    new_profile["acousticness"] = clamp(new_profile["acousticness"] + acoustic_level * 0.06)

    if acoustic_level > 0:
        new_profile["energy"] = clamp(new_profile["energy"] - acoustic_level * 0.03)

    return new_profile


def recommend_track(df, profile, seen_track_ids):
    candidates = df.copy()

    if seen_track_ids:
        candidates = candidates[~candidates["track_id"].isin(seen_track_ids)]

    if candidates.empty:
        candidates = df.copy()

    distance = 0

    for feature in FEATURE_COLUMNS:
        distance = distance + (candidates[feature] - profile[feature]) ** 2

    candidates["recommend_score"] = distance - (candidates["popularity"] / 100) * 0.03

    result = candidates.sort_values("recommend_score", ascending=True).iloc[0]

    return result