import os
from dotenv import load_dotenv

# LangChain and Ollama
from langchain_community.llms.ollama import Ollama
from langchain.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Supabase
from supabase import create_client

# Load env variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# LLM and embeddings
llm = Ollama(model="llama3:instruct", temperature=0)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Smart text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400,
    separators=["\n\n", "\n", ".", " "]
)

# Prompt template to reduce hallucination
qa_prompt = {
    "prompt": PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a helpful assistant. Use only the provided documents to answer the question.\n"
            "If the answer isn't available, respond with: 'Sorry, the information is not available.'\n\n"
            "Question: {question}\n\n"
            "Context:\n{context}\n\nAnswer:"
        )
    )
}

# ✅ Function 1: Single-file Q&A
def get_answer(file_name, query):
    file_path = os.path.join(working_dir, file_name)
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    print(f"[Single File] Loaded {len(documents)} docs")

    text_chunks = splitter.split_documents(documents)
    print(f"[Single File] Created {len(text_chunks)} chunks")

    knowledge_base = FAISS.from_documents(text_chunks, embeddings)

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=knowledge_base.as_retriever(),
        chain_type_kwargs=qa_prompt
    )

    response = qa_chain.invoke({"query": query})
    return response["result"]

# ✅ Function 2: Multi-file Q&A with persistent vectorstore
def get_answer_from_all_files(query):
    vectorstore_dir = os.path.join(working_dir, "vectorstore_index")

    if os.path.exists(os.path.join(vectorstore_dir, "index.faiss")):
        # ✅ Load saved vectorstore (with warning bypass)
        knowledge_base = FAISS.load_local(
            folder_path=vectorstore_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Loaded existing vectorstore from disk")
    else:
        # Rebuild vectorstore from Supabase files
        res = supabase.storage.from_(BUCKET_NAME).list("files/")
        file_list = [f['name'] for f in res if f['name'].endswith('.pdf')]
        all_docs = []

        for file_name in file_list:
            file_path = os.path.join(working_dir, file_name)

            file_bytes = supabase.storage.from_(BUCKET_NAME).download(f"files/{file_name}")
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            loader = PyMuPDFLoader(file_path)
            documents = loader.load()
            all_docs.extend(documents)

            os.remove(file_path)

        if not all_docs:
            return "No documents found in Supabase bucket."

        text_chunks = splitter.split_documents(all_docs)
        print(f"[All Files] Created {len(text_chunks)} chunks total")

        if not text_chunks:
            return "No meaningful content found in documents."

        knowledge_base = FAISS.from_documents(text_chunks, embeddings)

        # ✅ Save for reuse
        knowledge_base.save_local(vectorstore_dir)
        print("💾 Saved new vectorstore to disk")

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=knowledge_base.as_retriever(),
        chain_type_kwargs=qa_prompt
    )

    result = qa_chain.invoke({"query": query})
    return result["result"]
