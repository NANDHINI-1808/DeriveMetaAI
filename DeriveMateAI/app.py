import streamlit as st
import requests
import os

# 🔐 SAFE API KEY (from Streamlit / system environment)
API_KEY = os.getenv("OPENROUTER_API_KEY")

st.title("DERIVE META AI 🚀")
st.subheader("AI Engineering Exam Preparation Assistant")

topic = st.text_input("Enter Engineering Topic")

feature = st.selectbox(
    "Choose Feature",
    [
        "Explain Topic",
        "Generate 16 Mark Answer",
        "Generate Viva Questions"
    ]
)

if st.button("Generate"):

    if not API_KEY:
        st.error("API Key not found. Set OPENROUTER_API_KEY in environment variables.")
    
    elif topic == "":
        st.warning("Please enter a topic")

    else:

        # 🎯 Prompt creation
        if feature == "Explain Topic":
            prompt = f"Explain {topic} in simple engineering student language."

        elif feature == "Generate 16 Mark Answer":
            prompt = f"Generate detailed 16-mark university exam answer with derivation for {topic}."

        else:
            prompt = f"Generate important viva questions and answers for {topic}."

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

        # 🧠 SAFE OUTPUT
        if "choices" in result:
            st.success("Generated Successfully 🚀")
            st.write(result["choices"][0]["message"]["content"])
        else:
            st.error("Error from API")
            st.write(result)