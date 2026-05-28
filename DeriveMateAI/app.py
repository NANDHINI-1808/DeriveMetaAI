import streamlit as st
import requests
import os
from fpdf import FPDF

# 🔐 API KEY
API_KEY = os.getenv("OPENROUTER_API_KEY")

# 📜 HISTORY INIT
if "history" not in st.session_state:
    st.session_state.history = []

st.title("DERIVE META AI 🚀")
st.subheader("AI Engineering Exam Preparation Assistant")

# 📜 CHATGPT STYLE SIDEBAR HISTORY
st.sidebar.title("📜 Chat History")

if len(st.session_state.history) == 0:
    st.sidebar.info("No history yet")

for item in reversed(st.session_state.history):
    with st.sidebar.expander(f"{item['topic']} - {item['feature']}"):
        st.write(item["output"])

# INPUT
topic = st.text_input("Enter Engineering Topic")

feature = st.selectbox(
    "Choose Feature",
    [
        "Explain Topic",
        "Generate 16 Mark Answer",
        "Generate Viva Questions",
        "Generate Image",
        "Download PDF"
    ]
)

# 📄 PDF FUNCTION
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    file_path = "answer.pdf"
    pdf.output(file_path)
    return file_path


if st.button("Generate"):

    if not API_KEY:
        st.error("API Key not found. Set OPENROUTER_API_KEY in environment variables.")

    elif topic == "":
        st.warning("Please enter a topic")

    else:

        # 🎯 PROMPT BUILD
        if feature == "Explain Topic":
            prompt = f"Explain {topic} in simple engineering student language."

        elif feature == "Generate 16 Mark Answer":
            prompt = f"Generate detailed 16-mark university exam answer with derivation for {topic}."

        elif feature == "Generate Viva Questions":
            prompt = f"Generate important viva questions and answers for {topic}."

        elif feature == "Generate Image":
            prompt = f"Create a clean labeled engineering diagram explanation for {topic}. Make it simple and educational."

        else:
            prompt = f"Write detailed notes for {topic} suitable for PDF download."

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

        # 🧠 OUTPUT HANDLING
        if "choices" in result:
            output = result["choices"][0]["message"]["content"]

            st.success("Generated Successfully 🚀")

            # 🖼️ IMAGE FEATURE
            if feature == "Generate Image":
                st.image(
                    "https://source.unsplash.com/800x400/?" + topic,
                    caption=f"AI Visual for {topic}"
                )
            else:
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
            st.error("Error from API")
            st.write(result)
