import streamlit as st
import requests
import os
from fpdf import FPDF

# ================= API KEYS =================
API_KEY = os.getenv("OPENROUTER_API_KEY")

# OPTIONAL (for real image generation later)
IMAGE_KEY = os.getenv("STABILITY_API_KEY")

# ================= USERS =================
USERS = {
    "admin": "admin123",
    "student": "1234"
}

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat" not in st.session_state:
    st.session_state.chat = []

if "user" not in st.session_state:
    st.session_state.user = "Guest"

if "subject" not in st.session_state:
    st.session_state.subject = "EEE"

# ================= LOGIN =================
def login_page():
    st.title("🔐 DERIVE META AI")

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
        if st.button("Guest Mode"):
            st.session_state.logged_in = True
            st.session_state.user = "Guest"
            st.rerun()

# ================= PDF =================
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    file_path = "revision_booklet.pdf"
    pdf.output(file_path)
    return file_path

# ================= IMAGE PROMPT (REAL DIAGRAM AI) =================
def generate_image_prompt(text):
    return f"""
    Draw a clean engineering schematic / textbook diagram:
    Topic: {text}
    Style: black and white, labeled, circuit style, engineering textbook quality
    """

# ================= MAIN APP =================
def app():

    st.sidebar.title(f"👤 {st.session_state.user}")

    # SUBJECT SWITCH (MULTI DOMAIN AI)
    st.session_state.subject = st.sidebar.selectbox(
        "Select Branch",
        ["EEE", "ECE", "CSE", "MECH"]
    )

    st.sidebar.markdown("### 📜 History")

    for c in reversed(st.session_state.chat):
        st.sidebar.write("Q:", c["q"])
        st.sidebar.write("A:", c["a"][:40])
        st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🔥 DERIVE META AI - SUPER STUDY BRAIN")

    # ================= MODE =================
    mode = st.selectbox(
        "Choose Mode",
        [
            "Chat Question",
            "16 Mark Answer",
            "Short Notes",
            "Derivation Steps",
            "Circuit / Diagram Generator",
            "Exam Revision Booklet"
        ]
    )

    question = st.text_input("Ask Engineering Question")

    # ================= GENERATE =================
    if st.button("ASK AI"):

        if question == "":
            st.warning("Enter question")

        else:

            # ========== PROMPTS ==========
            base = f"Subject: {st.session_state.subject}. "

            if mode == "Chat Question":
                prompt = base + f"Explain like a teacher: {question}"

            elif mode == "16 Mark Answer":
                prompt = base + f"Write detailed 16-mark university answer: {question}"

            elif mode == "Short Notes":
                prompt = base + f"Give short revision notes: {question}"

            elif mode == "Derivation Steps":
                prompt = base + f"Step-by-step derivation: {question}"

            elif mode == "Circuit / Diagram Generator":
                prompt = base + generate_image_prompt(question)

            else:
                prompt = base + f"Create full exam revision booklet format: {question}"

            # ================= TEXT AI CALL =================
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            result = response.json()

            if "choices" in result:
                answer = result["choices"][0]["message"]["content"]

                st.success("AI Generated 🚀")
                st.write(answer)

                # SAVE CHAT
                st.session_state.chat.append({
                    "q": question,
                    "a": answer
                })

                # ================= PDF =================
                pdf_file = create_pdf(answer)
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 Download Revision Booklet", f, file_name="revision.pdf")

            else:
                st.error(result)

# ================= ROUTER =================
if st.session_state.logged_in:
    app()
else:
    login_page()
