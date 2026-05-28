import streamlit as st
import requests
import os
from fpdf import FPDF
import streamlit.components.v1 as components

# 🔐 API KEY
API_KEY = os.getenv("OPENROUTER_API_KEY")

# ---------------- USERS ----------------
USERS = {
    "admin": "admin123",
    "student": "1234"
}

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "user" not in st.session_state:
    st.session_state.user = ""

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 DERIVE META AI LOGIN")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid Credentials")

    with col2:
        if st.button("Continue as Guest"):
            st.session_state.logged_in = True
            st.session_state.user = "Guest"
            st.rerun()

# ---------------- LOGOUT ----------------
def logout():
    st.session_state.logged_in = False
    st.rerun()

# ---------------- PDF ----------------
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    file_path = "answer.pdf"
    pdf.output(file_path)
    return file_path

# ---------------- MAIN APP ----------------
def app_page():

    st.set_page_config(page_title="Derive Meta AI", layout="wide")

    st.sidebar.title(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        logout()

    # 📜 HISTORY
    st.sidebar.title("📜 History")
    for item in reversed(st.session_state.history):
        st.sidebar.write(f"**{item['feature']}**")
        st.sidebar.write(item["topic"])
        st.sidebar.markdown("---")

    st.title("DERIVE META AI 🚀")
    st.subheader("AI Engineering Exam Assistant")

    # ---------------- INPUT ----------------
    topic = st.text_input("Enter Engineering Topic")

    # ---------------- VOICE INPUT ----------------
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

    # ---------------- GENERATE ----------------
    if st.button("Generate"):

        if not API_KEY:
            st.error("API Key not found")

        elif topic == "":
            st.warning("Enter topic")

        else:

            # 🎯 PROMPTS
            if feature == "Explain Topic":
                prompt = f"Explain {topic} in simple engineering language"

            elif feature == "Generate 16 Mark Answer":
                prompt = f"Write detailed 16-mark university answer with derivation for {topic}"

            elif feature == "Generate Viva Questions":
                prompt = f"Give viva questions and answers for {topic}"

            elif feature == "Generate Image Idea":
                prompt = f"Create engineering diagram explanation for {topic}"

            else:
                prompt = f"Create exam notes for {topic}"

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

            # 🧠 OUTPUT
            if "choices" in result:
                output = result["choices"][0]["message"]["content"]

                st.success("Generated 🚀")
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
                st.error(result)

# ---------------- ROUTER ----------------
if st.session_state.logged_in:
    app_page()
else:
    login_page()
