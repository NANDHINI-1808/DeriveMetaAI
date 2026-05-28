import streamlit as st
import requests
import os
from fpdf import FPDF
import streamlit.components.v1 as components

# 🔐 API KEY
API_KEY = os.getenv("OPENROUTER_API_KEY")

# 📜 HISTORY
if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="Derive Meta AI", layout="wide")

# ---------------- SIDEBAR HISTORY ----------------
st.sidebar.title("📜 Chat History")

for item in reversed(st.session_state.history):
    st.sidebar.write(f"**{item['feature']}**")
    st.sidebar.write(item["topic"])
    st.sidebar.markdown("---")

# ---------------- TITLE ----------------
st.title("DERIVE META AI 🚀")
st.subheader("AI Engineering Exam Preparation Assistant")

# ---------------- INPUT ----------------
topic = st.text_input("Enter Engineering Topic")

# 🎤 VOICE INPUT (Chrome Web Speech API)
st.subheader("🎤 Voice Input")

voice_html = """
<button onclick="startDictation()">🎤 Speak</button>
<input id="text" style="width:100%;padding:10px;margin-top:10px;" placeholder="Voice text appears here">

<script>
function startDictation() {
    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = function(event) {
        document.getElementById('text').value =
        event.results[0][0].transcript;
    }
}
</script>
"""

components.html(voice_html, height=150)

# ---------------- FEATURE ----------------
feature = st.selectbox(
    "Choose Feature",
    [
        "Explain Topic",
        "Generate 16 Mark Answer",
        "Generate Viva Questions",
        "Generate Image Idea",
        "Download PDF"
    ]
)

# ---------------- PDF ----------------
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    file_path = "answer.pdf"
    pdf.output(file_path)
    return file_path

# ---------------- GENERATE ----------------
if st.button("Generate"):

    if not API_KEY:
        st.error("API Key not found")

    elif topic == "":
        st.warning("Enter topic first")

    else:

        # 🎯 PROMPT ENGINE
        if feature == "Explain Topic":
            prompt = f"Explain {topic} in simple engineering language"

        elif feature == "Generate 16 Mark Answer":
            prompt = f"Write detailed 16-mark university answer with derivation for {topic}"

        elif feature == "Generate Viva Questions":
            prompt = f"Give viva questions and answers for {topic}"

        elif feature == "Generate Image Idea":
            prompt = f"Create engineering diagram description for {topic}"

        else:
            prompt = f"Create detailed exam notes for {topic}"

        # 🌐 API CALL
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        result = response.json()

        # 🧠 OUTPUT SAFE
        if "choices" in result:
            output = result["choices"][0]["message"]["content"]

            st.success("Generated Successfully 🚀")
            st.write(output)

            # 📜 SAVE HISTORY
            st.session_state.history.append({
                "topic": topic,
                "feature": feature,
                "output": output
            })

            # 📄 PDF DOWNLOAD
            if feature == "Download PDF":
                pdf_file = create_pdf(output)
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 Download PDF", f, file_name="answer.pdf")

        else:
            st.error("API Error")
            st.write(result)

# ---------------- HISTORY ----------------
st.markdown("---")
st.subheader("📜 History")

for item in reversed(st.session_state.history):
    st.write("**Topic:**", item["topic"])
    st.write("**Feature:**", item["feature"])
    st.write(item["output"])
    st.markdown("---")
