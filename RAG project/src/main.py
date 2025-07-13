import os
import streamlit as st
from dotenv import load_dotenv
from doc_chat_utility import get_answer, get_answer_from_all_files
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
working_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="chat with doc",
    page_icon="📄",
    layout="centered"
)

st.title("Document Q&A - Llama 3 - ollama")

uploaded_file = st.file_uploader(label="Upload your file (optional)", type=["pdf"])
user_query = st.text_input("Ask your question")

if st.button("Run"):
    try:
        if not user_query.strip():
            st.warning("Please enter a question.")
            st.stop()

        #
        #  user uploaded a file
        if uploaded_file:
            bytes_data = uploaded_file.read()
            file_name = uploaded_file.name

            upload_response = supabase.storage.from_(BUCKET_NAME).upload(
                path=f"files/{file_name}",
                file=bytes_data,
                file_options={"content-type": "application/pdf"}
            )

            if upload_response is None:
                st.error("Upload failed: No response from Supabase.")
                st.stop()

            local_path = os.path.join(working_dir, file_name)
            with open(local_path, "wb") as f:
                f.write(bytes_data)

            answer = get_answer(file_name, user_query)
            st.success(answer)
            os.remove(local_path)

        # no upload, search all Supabase files
        else:
            st.info("No file uploaded. Searching all uploaded documents...")
            answer = get_answer_from_all_files(user_query)
            st.success(answer)

    except Exception as e:
        st.error(f"Error: {str(e)}")
