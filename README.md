# dev-rag-pilot
A mixed bag of development experiments, learning projects, and prototypes — from UI designs to backend logic.
# dev-rag-pilot

> A mixed bag of development experiments, learning projects, and prototypes — from UI designs to backend logic.

## 🚀 Overview

`dev-rag-pilot` is a learning-ground and experimental workspace for:
- Building RAG (Retrieval-Augmented Generation) applications
- Exploring LLMs like LLaMA 3 via Ollama
- Integrating Supabase for remote file storage
- Working with FAISS for vector search
- Using LangChain's utilities to build document-based Q&A systems

## 🧠 Features

- 📄 Upload and process PDF documents
- 🔍 Ask questions and get AI-powered answers from your documents
- 🧠 Uses LangChain + FAISS + HuggingFace for smart chunking & search
- ☁️ Stores and retrieves documents from Supabase buckets
- 🤖 Powered by LLaMA 3 (via Ollama)

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core programming language |
| **LangChain** | Orchestration of LLMs + vectorstores |
| **FAISS** | Efficient similarity search |
| **HuggingFace Transformers** | Text embeddings |
| **Supabase** | Cloud storage and remote PDFs |
| **Ollama** | Running LLaMA 3 locally |
| **PyMuPDF** | PDF loading |

## 📂 Project Structure

RAG project/
│
├── requirements.txt # Python dependencies
├── src/
│ ├── main.py # Streamlit app entry
│ ├── doc_chat_utility.py # Core QA functions
│ └── vectorstore_index/ # FAISS index files
├── .gitignore
└── README.md


## 🧪 How to Run

> ⚠️ Ensure you have Ollama installed and running with LLaMA 3.

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start the app (Streamlit)
streamlit run src/main.py
📦 Environment Setup
Create a .env file in the root with the following:

ini
Copy
Edit
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_service_role_key
SUPABASE_BUCKET=your_bucket_name
🔒 Security Note
This app uses FAISS vectorstore files that require allow_dangerous_deserialization=True.
Only run this on trusted files on your own machine.

🤝 License
No license selected yet. You’re free to view and learn from the code.
(Consider adding an MIT License if you want to allow re-use.)
