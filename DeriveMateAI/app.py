import streamlit as st
import requests
import os
from fpdf import FPDF
import urllib.parse

# ================= API KEY =================
API_KEY = os.getenv("OPENROUTER_API_KEY")

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
        if st.button("Guest Mode"):
            st.session_state.logged_in = True
            st.session_state.user = "Guest"
            st.rerun()

# ================= PDF =================
def create_pdf(question, answer, image_url=None):

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "DERIVE META AI - REVISION BOOKLET", ln=True, align="C")

    pdf.ln(10)

    # Question
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "QUESTION:", ln=True)

    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, question)

    pdf.ln(5)

    # Answer
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "ANSWER:", ln=True)

    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, answer)

    pdf.ln(5)

    # Image (Diagram)
    if image_url:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "DIAGRAM:", ln=True)

        try:
            import requests
            from io import BytesIO

            img_data = requests.get(image_url).content
            img_path = "diagram.png"

            with open(img_path, "wb") as f:
                f.write(img_data)

            pdf.image(img_path, x=10, w=180)

        except:
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 8, "Diagram could not be loaded")

    file_path = "revision.pdf"
    pdf.output(file_path)

    return file_path

# ================= 🔥 FIXED CIRCUIT DIAGRAM GENERATOR =================
def generate_circuit_diagram(topic):

    # VERY IMPORTANT: force strict schematic style
    prompt = f"""
    Clean engineering circuit diagram ONLY.
    Topic: {topic}

    Requirements:
    - black and white schematic
    - labeled components
    - no artistic style
    - textbook electrical engineering diagram
    - simple clean lines
    """

    encoded_prompt = urllib.parse.quote(prompt)

    # stable AI image generator
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux"

    return url

# ================= MAIN APP =================
def app():

    st.sidebar.title(f"👤 {st.session_state.user}")

    st.session_state.subject = st.sidebar.selectbox(
        "Select Branch",
        ["EEE", "ECE", "CSE", "MECH"]
    )

    st.sidebar.title("📜 History")

    for c in reversed(st.session_state.chat):
        st.sidebar.write("Q:", c["q"])
        st.sidebar.write("A:", c["a"][:50])
        st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🔥 DERIVE META AI - SMART STUDY BRAIN")

    mode = st.selectbox(
        "Choose Mode",
        [
            "Chat Question",
            "16 Mark Answer",
            "Short Notes",
            "Derivation Steps",
            "Circuit Diagram Generator"
        ]
    )

    question = st.text_input("Enter Engineering Question")

    if st.button("ASK AI"):

        if question == "":
            st.warning("Enter question")
            return

        # ================= CIRCUIT MODE =================
        if mode == "Circuit Diagram Generator":

            img_url = generate_circuit_diagram(question)

            st.success("Circuit Diagram Generated 🚀")

            st.image(img_url, caption="AI Generated Circuit Diagram")

            st.session_state.chat.append({
                "q": question,
                "a": "Circuit diagram generated"
            })

            return

        # ================= TEXT AI =================
        base = f"Subject: {st.session_state.subject}. "

        if mode == "Chat Question":
            prompt = base + f"Explain simply: {question}"

        elif mode == "16 Mark Answer":
            prompt = base + f"Write 16-mark exam answer: {question}"

        elif mode == "Short Notes":
            prompt = base + f"Give short notes: {question}"

        else:
            prompt = base + f"Step-by-step derivation: {question}"

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

            st.session_state.chat.append({
                "q": question,
                "a": answer
            })

            pdf_file = create_pdf(answer)
            with open(pdf_file, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name="revision.pdf")

        else:
            st.error(result)

# ================= ROUTER =================
if st.session_state.logged_in:
    app()
else:
    login_page()
