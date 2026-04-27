import streamlit as st
import pandas as pd


REQUIRED_COLUMNS = [
    "track_id",
    "artists",
    "album_name",
    "track_name",
    "popularity",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
    "track_genre",
]


@st.cache_data(show_spinner="음악 데이터를 불러오고 전처리하는 중입니다...")
def load_music_data():
    df = pd.read_csv("music_data.csv.gz", encoding="utf-8-sig")

    df.columns = (
        df.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    missing_columns = []

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing_columns.append(col)

    if missing_columns:
        raise ValueError(
            f"필수 컬럼이 없습니다: {missing_columns}\n"
            f"현재 파일 컬럼: {list(df.columns)}"
        )

    df = df[REQUIRED_COLUMNS]

    df = df.dropna()

    df = df.drop_duplicates(subset=["track_id"])

    numeric_columns = [
        "popularity",
        "danceability",
        "energy",
        "loudness",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "time_signature",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    loudness_min = df["loudness"].min()
    loudness_max = df["loudness"].max()

    if loudness_max != loudness_min:
        df["loudness_norm"] = (df["loudness"] - loudness_min) / (loudness_max - loudness_min)
    else:
        df["loudness_norm"] = 0.5

    tempo_min = df["tempo"].min()
    tempo_max = df["tempo"].max()

    if tempo_max != tempo_min:
        df["tempo_norm"] = (df["tempo"] - tempo_min) / (tempo_max - tempo_min)
    else:
        df["tempo_norm"] = 0.5

    df = df.reset_index(drop=True)

    return df