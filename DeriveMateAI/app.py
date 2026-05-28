import streamlit as st
import requests
import os
from fpdf import FPDF
from PIL import Image

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

# ---------------- MAIN UI ----------------
st.title("DERIVE META AI 🚀")
st.subheader("AI Engineering Exam Assistant")

# INPUT
topic = st.text_input("Enter Engineering Topic")

# FEATURE
feature = st.selectbox(
    "Choose Feature",
    [
        "Explain Topic",
        "Generate 16 Mark Answer",
        "Generate Viva Questions",
        "Generate Image Idea",
        "Voice Input",
        "Upload Image",
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


# ---------------- VOICE INPUT (Browser-safe fallback) ----------------
if feature == "Voice Input":
    st.info("Use Chrome voice input (recommended Streamlit Cloud safe)")
    st.markdown("""
    👉 Use this instead:
    - Right click → Voice typing in Chrome
    - Paste text into topic box
    """)

# ---------------- IMAGE UPLOAD ----------------
uploaded_file = None
if feature == "Upload Image":
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        topic = "Analyze this image and explain engineering concept"

# ---------------- BUTTON ----------------
if st.button("Generate"):

    if not API_KEY:
        st.error("API Key not found")

    elif topic == "":
        st.warning("Enter topic first")

    else:

        # 🎯 PROMPTS
        if feature == "Explain Topic":
            prompt = f"Explain {topic} in simple engineering language"

        elif feature == "Generate 16 Mark Answer":
            prompt = f"Write detailed 16 mark exam answer with derivation for {topic}"

        elif feature == "Generate Viva Questions":
            prompt = f"Give viva questions and answers for {topic}"

        elif feature == "Generate Image Idea":
            prompt = f"Create engineering diagram description for {topic}"

        elif feature == "Upload Image":
            prompt = "Explain uploaded engineering image in detail"

        elif feature == "Download PDF":
            prompt = f"Create exam notes for {topic}"

        else:
            prompt = f"Explain {topic}"

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

            st.success("Generated Successfully 🚀")
            st.write(output)

            # 📜 SAVE HISTORY
            st.session_state.history.append({
                "topic": topic,
                "feature": feature,
                "output": output
            })

            # 📄 PDF
            if feature == "Download PDF":
                pdf_file = create_pdf(output)
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 Download PDF", f, file_name="answer.pdf")

        else:
            st.error("API Error")
            st.write(result)
