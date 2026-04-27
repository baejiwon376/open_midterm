import json
import os
import streamlit as st


PROFILE_FILE = "user_profiles.json"


@st.cache_data
def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}

    with open(PROFILE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        json.dump(profiles, file, ensure_ascii=False, indent=4)

    load_profiles.clear()


def load_user_profile(username):
    profiles = load_profiles()
    return profiles.get(username)


def save_user_profile(username, profile_data):
    profiles = load_profiles()
    profiles[username] = profile_data
    save_profiles(profiles)