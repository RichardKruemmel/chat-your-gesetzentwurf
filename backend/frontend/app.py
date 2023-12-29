import streamlit as st
import requests

st.set_page_config(
    page_title="Chat Your Election Program", page_icon="💬", layout="centered"
)


@st.cache_data(ttl=3600)
def get_available_programs():
    try:
        response = requests.get("http://127.0.0.1:8000/vectorized-programs")
        if response.status_code == 200:
            vectorized_programs = response.json()
            return vectorized_programs
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None


with st.sidebar:
    st.title("Available Election Programs")
    vectorized_programs = get_available_programs()
    if vectorized_programs is not None:
        for program in vectorized_programs:
            st.write(f"{program['full_name']} ({program['label']})")
    else:
        st.write("No election programs available.")
    "[View the source code](https://github.com/RichardKruemmel/chat-your-gesetzentwurf)"

st.title("Chat Your Election Program")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your election program expert."}
    ]

if "input" not in st.session_state:
    st.session_state["input"] = ""


def on_send():
    user_input = st.session_state["input"]
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        api_response = send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": api_response})
    st.session_state["input"] = ""


def send_message(message):
    api_url = "http://127.0.0.1:8000/chat_llama"
    response = requests.post(api_url, json={"question": message})
    response_json = response.json()
    return response_json["reply"]["response"]


for message in st.session_state.messages:
    if message["role"] == "user":
        st.text_area(
            label="User input",
            value=message["content"],
            key=message["content"],
            height=50,
            disabled=True,
        )
    else:
        st.text_area(
            label="AI response",
            value=message["content"],
            key=message["content"],
            height=100,
            disabled=True,
        )

user_input = st.text_input(
    "Your question", key="input", value=st.session_state["input"]
)

if st.button("Send", on_click=on_send):
    pass
