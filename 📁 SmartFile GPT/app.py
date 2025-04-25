
import streamlit as st
import pandas as pd
import requests

# Streamlit UI
st.title("📁 SmartFile GPT :)")

uploaded_file = st.file_uploader("Upload a CSV, Excel, or JSON file", type=["csv", "xlsx", "json"])
user_query = st.text_area("🔍 Ask a question about your data")

llm_endpoint = st.sidebar.text_input("🧠 Local LLM Endpoint", value="http://localhost:1245/v1/chat/completions")

df = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)

        st.subheader("📊 Data Preview")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}")

if df is not None and user_query:
    with st.spinner("Thinking..."):
        # Send table context and query to local LLM
        context = df.head(10).to_string(index=False)
        prompt = f"You are a helpful data analyst. Given this data table:{context}Answer the following question:{user_query}"
        payload = {
            "model": "local-llm",  # LM Studio/Ollama model name if needed
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        try:
            response = requests.post(llm_endpoint, json=payload, timeout=60)
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                st.success("✅ Answer:")
                st.write(answer)
            else:
                st.error(f"LLM error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"❌ Failed to contact local LLM: {e}")
