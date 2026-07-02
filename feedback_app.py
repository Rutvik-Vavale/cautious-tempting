import datetime
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="Smart Atmosphere Feedback",
    page_icon="🌡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

FEEDBACK_MAP = {
    1: {"emoji": "🥶", "label": "Chill", "text": "Workspace feels too cold."},
    2: {"emoji": "😌", "label": "Cool", "text": "Slightly cool but manageable."},
    3: {"emoji": "🙂", "label": "Comfortable", "text": "Temperature feels balanced."},
    4: {"emoji": "😓", "label": "Warm", "text": "Temperature feels a bit warm."},
    5: {"emoji": "🥵", "label": "Too Hot", "text": "Workspace feels too hot."},
}

LATITUDE = 22.3072
LONGITUDE = 73.1812
LOCATION_LABEL = "LTTS Vadodara"

if "employee_id" not in st.session_state:
    st.session_state.employee_id = ""
if "comfort_level" not in st.session_state:
    st.session_state.comfort_level = 3
if "show_thanks" not in st.session_state:
    st.session_state.show_thanks = False
if "submitted_name" not in st.session_state:
    st.session_state.submitted_name = ""


@st.cache_data(ttl=900)
def get_vadodara_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        "&current=temperature_2m,apparent_temperature,weather_code"
    )
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current", {})
    return {
        "temperature": current.get("temperature_2m"),
        "apparent_temperature": current.get("apparent_temperature"),
        "weather_code": current.get("weather_code"),
    }


def weather_code_to_text(code):
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Rain showers",
        95: "Thunderstorm",
    }
    return mapping.get(code, "Weather update available")


def post_to_google_sheet(row_data):
    if "apps_script_url" not in st.secrets:
        raise RuntimeError("Missing apps_script_url in Streamlit secrets.")

    response = requests.post(
        st.secrets["apps_script_url"],
        json=row_data,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def reset_form():
    st.session_state.employee_id = ""
    st.session_state.comfort_level = 3
    st.session_state.show_thanks = False
    st.session_state.submitted_name = ""


try:
    weather = get_vadodara_weather()
    weather_temp = weather["temperature"]
    apparent_temp = weather["apparent_temperature"]
    weather_text = weather_code_to_text(weather["weather_code"])
    weather_ok = True
except Exception:
    weather_temp = None
    apparent_temp = None
    weather_text = "Unavailable"
    weather_ok = False

st.markdown(
    """
    <style>
    .app-card {
        background: #ffffff;
        border: 1px solid #dde7ec;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 26px rgba(23, 48, 66, 0.06);
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #173042;
        margin-bottom: 0.35rem;
    }
    .hero-copy {
        color: #5f7482;
        font-size: 0.98rem;
        line-height: 1.55;
    }
    .emoji-card {
        text-align: center;
        padding: 18px;
        border-radius: 16px;
        background: #f7fbfc;
        border: 1px solid #dfe8ec;
        margin-top: 8px;
        margin-bottom: 10px;
    }
    .emoji-face {
        font-size: 3.7rem;
        line-height: 1;
        margin-bottom: 0.45rem;
    }
    .emoji-label {
        font-size: 1.15rem;
        font-weight: 700;
        color: #173042;
        margin-bottom: 0.15rem;
    }
    .emoji-copy {
        color: #667986;
        font-size: 0.95rem;
    }
    .thanks-card {
        text-align: center;
        padding: 34px 24px;
        border-radius: 22px;
        background: #ffffff;
        border: 1px solid #dbe5ea;
        box-shadow: 0 14px 36px rgba(23, 48, 66, 0.08);
        margin-top: 34px;
    }
    .thanks-icon {
        font-size: 4rem;
        margin-bottom: 0.5rem;
    }
    .thanks-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #173042;
        margin-bottom: 0.45rem;
    }
    .thanks-copy {
        color: #607482;
        font-size: 1rem;
        line-height: 1.6;
    }
    .tiny-note {
        color: #718490;
        font-size: 0.84rem;
        margin-top: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.show_thanks:
    st.markdown(
        f"""
        <div class="thanks-card">
            <div class="thanks-icon">✅</div>
            <div class="thanks-title">Thank you</div>
            <div class="thanks-copy">{st.session_state.submitted_name}, your feedback has been recorded successfully.</div>
            <div class="tiny-note">This screen will refresh automatically in 5 seconds for the next response.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(5)
    reset_form()
    st.rerun()

selected = FEEDBACK_MAP[st.session_state.comfort_level]

st.markdown(
    """
    <div class="app-card">
        <div class="hero-title">Smart Atmosphere Feedback</div>
        <div class="hero-copy">Please enter your employee ID for this demo and select the temperature comfort level that matches your current experience.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.text_input("Employee ID", placeholder="e.g. EMP1042", key="employee_id")
st.slider(
    "Temperature feedback",
    min_value=1,
    max_value=5,
    key="comfort_level",
    help="1 = Chill, 5 = Too Hot",
)

selected = FEEDBACK_MAP[st.session_state.comfort_level]

st.markdown(
    f"""
    <div class="emoji-card">
        <div class="emoji-face">{selected['emoji']}</div>
        <div class="emoji-label">Level {st.session_state.comfort_level}: {selected['label']}</div>
        <div class="emoji-copy">{selected['text']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("1 = Chill   |   3 = Comfortable   |   5 = Too Hot")

if st.button("Submit feedback", type="primary", use_container_width=True):
    if not st.session_state.employee_id.strip():
        st.error("Please enter Employee ID before submitting.")
    else:
        now = datetime.datetime.now()
        payload = {
            "employeeId": st.session_state.employee_id.strip(),
            "tempFeedbackValue": st.session_state.comfort_level,
            "tempFeedbackLabel": selected["label"],
            "emoji": selected["emoji"],
            "submittedAtISO": now.isoformat(),
            "submittedAtLocal": now.strftime("%Y-%m-%d %H:%M:%S"),
            "weatherTempC": weather_temp if weather_ok else "Unavailable",
            "apparentTempC": apparent_temp if weather_ok else "Unavailable",
            "weatherCondition": weather_text,
            "location": LOCATION_LABEL,
        }
        try:
            result = post_to_google_sheet(payload)
            if result.get("success"):
                st.session_state.submitted_name = st.session_state.employee_id.strip()
                st.session_state.show_thanks = True
                st.rerun()
            else:
                st.error("The sheet did not confirm success. Check the Apps Script deployment.")
        except Exception as exc:
            st.error(f"Submission failed: {exc}")

st.divider()
st.caption(
    "Your response is used for workplace comfort analysis. For the demo, employee ID is entered manually instead of being filled from company login."
)
