import streamlit as st
import requests
import os
from fpdf import FPDF

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

if "chat" not in st.session_state:
    st.session_state.chat = []

if "user" not in st.session_state:
    st.session_state.user = "Guest"

# ---------------- LOGIN ----------------
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

# ---------------- PDF ----------------
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    file_path = "notes.pdf"
    pdf.output(file_path)
    return file_path

# ---------------- MAIN APP ----------------
def app():

    st.sidebar.title(f"👤 {st.session_state.user}")

    # 📜 CHAT HISTORY
    st.sidebar.title("📜 History")
    for c in reversed(st.session_state.chat):
        st.sidebar.write(f"Q: {c['q']}")
        st.sidebar.write(f"A: {c['a'][:40]}...")
        st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🔥 DERIVE META AI - STUDY SUPER BRAIN")

    # ---------------- MODE ----------------
    mode = st.selectbox(
        "Choose Study Mode",
        [
            "Chat Question",
            "16 Mark Answer",
            "Short Notes",
            "Derivation Steps",
            "Image Diagram Idea"
        ]
    )

    # ---------------- INPUT ----------------
    question = st.text_input("Ask your Engineering Question")

    # ---------------- GENERATE ----------------
    if st.button("ASK AI"):

        if question == "":
            st.warning("Enter question")

        else:

            # 🎯 SMART PROMPTS
            if mode == "Chat Question":
                prompt = f"Explain simply like teacher: {question}"

            elif mode == "16 Mark Answer":
                prompt = f"Write detailed 16-mark exam answer with headings: {question}"

            elif mode == "Short Notes":
                prompt = f"Give short revision notes: {question}"

            elif mode == "Derivation Steps":
                prompt = f"Explain step-by-step derivation: {question}"

            else:
                prompt = f"Give engineering diagram description for image generation: {question}"

            # 🌐 API CALL
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

                # 💾 SAVE CHAT
                st.session_state.chat.append({
                    "q": question,
                    "a": answer
                })

                # 📄 PDF DOWNLOAD
                pdf_file = create_pdf(answer)
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 Download Notes PDF", f, file_name="notes.pdf")

            else:
                st.error(result)

# ---------------- ROUTER ----------------
if st.session_state.logged_in:
    app()
else:
    login_page()
