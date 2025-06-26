import streamlit as st
import requests
from rag_utils import query_rag
import ollama

# 👇 Manually configure Gemini API key here
# configure_gemini_key("AIzaSyDRyNnzXXib-0bHBh1iRDbYOoGUF_PMPvY")

st.set_page_config(page_title="AI Grievance Chatbot", page_icon="🤖")
st.title("AI Grievance Chatbot")

BASE_URL = "http://127.0.0.1:8000"  


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [("bot", " Hi! How may I help you today?")]
if "step" not in st.session_state:
    st.session_state.step = "awaiting_intent"
if "complaint_data" not in st.session_state:
    st.session_state.complaint_data = {
        "complaint": None,
        "name": None,
        "mobile": None,
        "complaint_id": None
    }

#  Intent detection
import ollama

def detect_intent_llm(text):
    print(text)
    prompt = f"""
You are an assistant that classifies user messages into intents. The only possible intents are:
- "register" → for registering or raising a complaint
- "status" → for checking complaint status
- "rag" → for policy, warranty, or information queries
- "unknown" → if it doesn't fit any above

Only reply with one of: register, status, rag, or unknown.Reply should be in single word ONLY

Message: "{text}"
Intent:"""

    try:
        response = ollama.chat(

            model='phi3',
            options={
        "temperature": 0.3,

    },
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip().lower()
    except Exception as e:
        print(" LLM Intent Detection Error:", e)
        return "unknown"


# API to register complaint
def register_complaint_api(data):
    try:
        res = requests.post(f"{BASE_URL}/register", json=data)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# API to check complaint status
def get_status(complaint_id):
    try:
        res = requests.post(f"{BASE_URL}/status", json={"complaint_id": complaint_id})
        return res.json()
    except Exception as e:
        return {"error": str(e)}

#  Chat input handling
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    step = st.session_state.step
    data = st.session_state.complaint_data
    bot_reply = ""

    # Step: Detect intent
    if step == "awaiting_intent":
        user_text = user_input.lower().strip()
        if user_text in ["no", "no thanks", "nothing", "nah"]:
            bot_reply = " Thank you for reaching out. Have a great day!"
        else:
            intent = detect_intent_llm(user_input)
            print(intent,"Intent---------------------")
            if intent == "register":
                st.session_state.step = "ask_reason"
                data.update({"complaint": None, "name": None, "mobile": None, "complaint_id": None})
                bot_reply = "Sure! Please describe your issue."
            elif intent == "status":
                st.session_state.step = "ask_complaint_id"
                bot_reply = "Please provide your Complaint ID to check the status."
            elif intent == "rag":
                answer = query_rag(user_input)
                bot_reply = f" {answer}\n\n Anything else I can help you with?"
            else:
                bot_reply = "I can help you register a complaint, check status, or answer policy-related questions."

    # Step: Register flow
    elif step == "ask_reason":
        data["complaint"] = user_input
        st.session_state.step = "ask_name"
        bot_reply = "Got it. Can I have your name, please?"

    elif step == "ask_name":
        data["name"] = user_input
        st.session_state.step = "ask_mobile"
        bot_reply = "Thanks. What is your mobile number?"

    elif step == "ask_mobile":
        data["mobile"] = user_input
        response = register_complaint_api(data)
        if "complaint_id" in response:
            data["complaint_id"] = response["complaint_id"]
            bot_reply = f" Complaint registered successfully!\n\n Complaint ID: `{data['complaint_id']}`\n\n Anything else I can help you with?"
        else:
            bot_reply = " Something went wrong while registering your complaint."
        st.session_state.step = "awaiting_intent"

    # Step: Status check
    elif step == "ask_complaint_id":
        complaint_id = user_input.strip()
        response = get_status(complaint_id)
        if "error" in response:
            bot_reply = " Could not find any complaint with that ID."
        else:
            status = response.get("status", "Unknown")
            bot_reply = f" Complaint Status: **{status}**\n\n Anything else I can help you with?"
        st.session_state.step = "awaiting_intent"

    else:
        bot_reply = " I'm here to help. Say 'register complaint', 'check status', or ask a policy question."

    st.session_state.chat_history.append(("bot", bot_reply))

# Display the chat conversation
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)
