# Academic Assistant Chatbot

## Description

An intelligent academic assistant chatbot for the Universidad Nacional de Colombia, Manizales campus. This project provides students with quick access to information about the academic curriculum, course descriptions, schedules, professors, and classroom assignments through a conversational interface powered by RAG (Retrieval-Augmented Generation) technology.

The system combines semantic search with AI-powered response generation to deliver accurate and contextual answers about academic programs, courses, prerequisites, and scheduling information.

**Technologies Used:**

- **LLM**: OpenAI GPT-5-mini for response generation
- **Embeddings**: OpenAI text-embedding-3-small for semantic search
- **Vector Database**: ChromaDB for storing document embeddings


##  Quick Start

### Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/miocampol/SIC-final-project-monorepo.git
cd SIC-final-project-monorepo
```


### Prerequisites

**Backend:**

- Python 3.12 or higher
- OpenAI API key

**Frontend:**

- Node.js 18 or higher
- npm 

## Installation & Setup

### Backend

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Windows (Git Bash)**: `source venv/Scripts/activate`
   - **Windows (CMD)**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

6. Load documents into the RAG system:
   ```bash
   python cargar_chroma.py
   ```

### Frontend

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

##  Running the Project

### Backend

Start the FastAPI server:

```bash
cd backend
source venv/Scripts/activate  # Activate virtual environment (Windows Git Bash)
python main.py
```

The backend API will be available at: **http://localhost:8000**

- API Documentation: http://localhost:8000/docs


### Frontend

Start the development server:

```bash
cd frontend
npm run dev
```

The frontend application will be available at: **http://localhost:5173**

