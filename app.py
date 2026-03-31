import streamlit as st
from google import genai
from google.genai import errors
import base64
from PIL import Image
import io
import time

# --- CONFIGURATION ---
# It is highly recommended to use st.secrets["GEMINI_API_KEY"] for deployment
API_KEY = "AIzaSyCky2CePCfviPp7DoibQeoX7EhP-Ou721A"
client = genai.Client(api_key=API_KEY)

st.set_page_config(
    page_title="Aetheris Image Lab",
    page_icon="🔮",
    layout="wide"
)

# --- AETHERIS GLASSMORPHIC STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp {
        background-color: #000000;
        color: white;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .accent-text {
        color: #00ffff;
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    .stButton>button {
        background: rgba(255, 255, 255, 0.03);
        color: #00ffff;
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 12px;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        border-color: #00ffff;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- IMAGE GENERATION LOGIC ---
def generate_artifact(prompt, aspect_ratio, high_detail):
    enhanced_prompt = f"""
    Style: Glassmorphic sci-fi mechanical technology digital art.
    Mood: futuristic, semi-transparent, monochromatic.
    Background: Deep black (#000000).
    Subject: {prompt}
    {"Include intricate complex internal glass structures." if high_detail else ""}
    """.strip()

    # Retry logic for rate limits
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model = genai.GenerativeModel('gemini-1.5-flash')
                contents=enhanced_prompt,
                config={
                    'image_config': {
                        'aspect_ratio': aspect_ratio
                    }
                }
            )
            
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data
            return None
            
        except errors.ClientError as e:
            if "429" in str(e) and attempt < max_retries:
                time.sleep(5) # Wait 5 seconds before retrying
                continue
            raise e

# --- UI LAYOUT ---
st.sidebar.markdown("<h1 style='color: #00ffff;'>AETHERIS</h1>", unsafe_allow_html=True)
aspect_ratio = st.sidebar.selectbox("Aspect Ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
high_detail = st.sidebar.checkbox("High Detail Matrix")

st.title("Neural Materialization Lab")

if prompt := st.chat_input("Describe a mechanical device..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Materializing artifact...", expanded=True) as status:
            try:
                image_data = generate_artifact(prompt, aspect_ratio, high_detail)
                if image_data:
                    img = Image.open(io.BytesIO(base64.b64decode(image_data)))
                    st.image(img, use_container_width=True)
                    status.update(label="Materialization Complete", state="complete")
                else:
                    st.error("Neural link interrupted: No image data returned.")
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ **Quota Exhausted:** The Gemini 2.5 Flash Image model has reached its limit for this API key. This model often requires a billing account to be linked in Google AI Studio, even for the free tier.")
                    st.info("Check your limits at: https://aistudio.google.com/app/plan")
                else:
                    st.error(f"Materialization failed: {str(e)}")
