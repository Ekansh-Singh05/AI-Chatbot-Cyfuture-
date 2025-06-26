# Chatbot Project

## Overview

This chatbot is developed to handle the following core functionalities:

1. **Register a Complaint**
2. **Check the Status of a Complaint**
3. **Answer Queries Related to Policies (RAG)**

---

## Frontend

The frontend of the chatbot is built using **Streamlit**.

- Bot responses are shown with a bot icon.
- User messages are shown with a user icon.

---

## Database

The chatbot uses **Firebase Firestore** to store:
- User details
- Complaint issues
- Complaint status

---

## Workflow

1. When the user starts the chatbot, it prompts:
   > "How may I help you?"

2. Based on the user's message, the chatbot detects the **intent** using a **Large Language Model (LLM)**.

3. **Intent Detection** is powered by the **Phi-3 model** from Microsoft, running locally using the **Ollama** library.

4. The chatbot supports four types of intents:
   - **Register**: To register a new complaint.
   - **Status**: To check the status of a previously registered complaint.
   - **RAG**: To ask questions about warranty, refund, support, and other policies.
   - **Unknown**: If the message doesn't match the above intents, a default response is shown.

---

## Intent Logic

### 1. Register

- Once the "register" intent is detected:
  - The bot prompts the user to describe the issue.
  - Then asks for the user's **name** and **mobile number**.
  - These details are saved using the **Register API**, which stores them in **Firebase Firestore**.
  - A unique **Complaint ID** is generated and shared with the user.

### 2. Status

- When the "status" intent is detected:
  - The bot prompts the user to enter the **Complaint ID**.
  - The **Status API** is called to retrieve and display the complaint status from the database.
  - If the ID is not found, a message indicating so is displayed.

### 3. RAG (Retrieval-Augmented Generation)

- For RAG queries:
  - Embeddings of sample policy documents are generated using the **all-minilm** model via **Ollama**.
  - A FAISS index is created and saved as a `.pkl` file.
  - The user's query is embedded using the same model and matched against the index.
  - The top-matching policy is used to respond to the user's query.

---

## Technologies Used

| Technology     | Purpose                                      |
|----------------|----------------------------------------------|
| Streamlit      | Frontend interface                           |
| Firebase       | Backend storage (Firestore)                  |
| FAISS          | Vector search for RAG                        |
| Ollama         | Local LLM runtime (for Phi-3 & embeddings)   |
| all-minilm     | Lightweight embedding model                  |
| Phi-3          | Intent detection LLM                         |
| Python         | Core programming language                    |

---

## Setup Instructions

1. Install [Ollama](https://ollama.com/) and pull the required models:
   ```bash
   ollama pull microsoft/phi3
   ollama pull all-minilm

2. pip install -r requirements.txt

## To run API (Status and Register APIs)
3. python main.py

## To run Chatbot UI
4. streamlit run chatbot_ui.py    
