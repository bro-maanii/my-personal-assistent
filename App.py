
import time
from openai import OpenAI
import openai
import streamlit as st
from openai.types.beta import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.thread_message import ThreadMessage

st.set_page_config(
   page_title="Cool ChatBot App",
   page_icon="🤖",

)
st.title("MY ASSISENT BOT🤖")

st.info("Welcome to MyChatBot! This chat bot is designed to help you with any questions or concerns regarding my professional life. Feel free to ask questions or engage in conversation. Please note that this is a demo version, and the bot's responses are generated based on your input.")

def clear_chat():
    with st.spinner(text="Clearing chat..."):
        if 'thread' not in st.session_state:
            st.session_state.thread = st.session_state.client.beta.threads.create()
        # Delete the existing thread
        st.session_state.client.beta.threads.delete(thread_id=st.session_state.thread.id)

        # Create a new thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

    st.success("Chat Cleared!")

def display_message(role, content):
    if role == "user":
        st.image("user-profile.png", width=50 , caption="User")
        st.info(content)
    elif role == "assistant":
        st.image("AI_icon.png", width=50 ,caption="AI")
        st.success(content)
    

def main():
    if 'client' not in st.session_state:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        st.session_state.client = openai.OpenAI()
        
    # Upload a file with an "assistants" purpose
        st.session_state.file = client.files.create(
        file=open("My-Info.pdf", "rb"),
        purpose='assistants'
        )
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
        name="Customer Service Assistant",
        instructions="you are my personal assisent who have all detail about me now you can help others with any query regarding me!",
        model="gpt-3.5-turbo-1106",
        tools=[{"type": "retrieval"}],
        file_ids=[st.session_state.file.id]
        )

        st.session_state.thread  = st.session_state.client.beta.threads.create()

    user_query = st.text_input("Enter your query:", key="user_query")
    
    if st.button("SUBMIT", key="submit"):
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=user_query
        )

        run= st.session_state.client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
        instructions="Please address the user as my future client. The user has asked you a question. You should respond to the user in a professional manner." )
       
        while True:
            # Wait for 5 seconds
            with st.spinner(text="In progress"):
                time.sleep(6)

            # Retrieve the run status
            run_status = st.session_state.client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )

            # If run is completed, get messages
            if run_status.status == 'completed':
                messages = st.session_state.client.beta.threads.messages.list(
                    thread_id=st.session_state.thread.id
                )

                # Loop through messages and print content based on role
                for msg in messages.data:
                    role = msg.role
                    content = msg.content[0].text.value
                    display_message(role, content)
                break
            else:
                with st.spinner(text="Waiting for the Assistant to process..."):
                    time.sleep(8)
                
    st.button("CLEAR CHAT", on_click=clear_chat)
                
if __name__ == "__main__":
    main()