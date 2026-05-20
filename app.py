import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from src.agents.orchestrator import ask
from src.evaluation.evaluator import evaluate_response

st.set_page_config(
    page_title="MedNova Health Agent",
    page_icon="🏥",
    layout="wide"
)

st.title("MedNova Hospital Chennai")
st.subheader("AI Health Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about patients, beds, medicines, appointments, or hospital policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("MedNova AI is thinking..."):
            result = ask(prompt, chat_history=st.session_state.chat_history)
            answer = result["answer"]
            agent_route = result["agent_route"]
            sources = result["sources"]
            scores = evaluate_response(prompt, answer, agent_route, sources)

        st.markdown(answer)

        with st.expander("Response Details"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Answer Quality", f"{scores.get('answer_quality', 0)}/5")
            col2.metric("Faithfulness", f"{scores.get('faithfulness', 0)}/5")
            col3.metric("Relevancy", f"{scores.get('relevancy', 0)}/5")
            st.write(f"Agent used: `{agent_route}`")
            st.write(f"Sources: {sources}")
            st.write(f"Routing correct: {scores.get('routing_correct', False)}")
            st.write(f"Feedback: {scores.get('feedback', '')}")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
