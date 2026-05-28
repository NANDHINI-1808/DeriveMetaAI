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

# ================= LOGIN =================
def login_page():
    st.title("🔐 DERIVE META AI LOGIN")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ================= DIAGRAM GENERATOR =================
def generate_diagram(topic):

    prompt = f"""
    Clean engineering diagram for: {topic}
    - labeled
    - black and white
    - textbook style
    - circuit / physics schematic
    """

    encoded = urllib.parse.quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux"

    return url

# ================= FIXED PDF =================
def create_pdf(question, answer, image_url=None):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "DERIVE META AI - REVISION SHEET", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "QUESTION:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, question)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "ANSWER:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, answer)

    # IMAGE ADD
    if image_url:
        try:
            import requests
            from io import BytesIO

            img = requests.get(image_url).content
            with open("diagram.png", "wb") as f:
                f.write(img)

            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "DIAGRAM:", ln=True)
            pdf.image("diagram.png", w=180)

        except:
            pass

    file_path = "revision.pdf"
    pdf.output(file_path)

    return file_path

# ================= MAIN APP =================
def app():

    st.sidebar.title(f"👤 {st.session_state.user}")

    st.title("🔥 DERIVE META AI - FINAL STUDY BRAIN")

    mode = st.selectbox(
        "Choose Mode",
        [
            "Chat Answer",
            "16 Mark Answer",
            "Short Notes",
            "Amperes Law Diagram Generator"
        ]
    )

    question = st.text_input("Enter your question")

    if st.button("GENERATE"):

        if question == "":
            st.warning("Enter question")
            return

        # ================= DIAGRAM MODE =================
        if mode == "Amperes Law Diagram Generator":

            img_url = generate_diagram(question)

            st.image(img_url, caption="AI Generated Diagram 🚀")

            answer = f"Diagram generated for {question}"

            st.session_state.chat.append({"q": question, "a": answer})

            pdf_file = create_pdf(question, answer, img_url)

            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, file_name="notes.pdf")

            return

        # ================= TEXT AI =================
        prompt = f"Explain in engineering exam format: {question}"

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

            st.success("Generated 🚀")
            st.write(answer)

            st.session_state.chat.append({"q": question, "a": answer})

            # FIXED PDF CALL ✅
            pdf_file = create_pdf(question, answer)

            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, file_name="notes.pdf")

        else:
            st.error(result)

# ================= ROUTE =================
if st.session_state.logged_in:
    app()
else:
    login_page()
