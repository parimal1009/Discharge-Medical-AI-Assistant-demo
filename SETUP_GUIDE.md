# Complete Setup Guide

## Step-by-Step Installation

### Step 1: System Requirements

Ensure you have:
- Python 3.8 or higher
- pip (Python package manager)
- 2GB free disk space
- Internet connection

Check Python version:
```bash
python --version
```

### Step 2: Download/Clone Project

If you have the project folder, navigate to it:
```bash
cd C:/Users/parim/Desktop/DATASMITH
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (Web framework)
- LangChain & Groq (AI agents)
- ChromaDB (Vector database)
- Sentence Transformers (Embeddings)
- And other required packages

**Note**: Installation may take 5-10 minutes depending on your internet speed.

### Step 5: Get API Keys

#### Groq API Key (Required)

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_...`)

#### Tavily API Key (Optional - for web search)

1. Go to https://tavily.com
2. Sign up for an account
3. Get your API key from dashboard
4. Copy the key

### Step 6: Configure Environment

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Open `.env` in a text editor (Notepad, VS Code, etc.)

3. Add your API keys:
```env
GROQ_API_KEY=gsk_your_actual_key_here
TAVILY_API_KEY=tvly_your_actual_key_here
```

4. Save the file

### Step 7: Run the Application

```bash
python run.py
```

You should see:
```
============================================================
Post Discharge Medical AI Assistant - Setup
============================================================
✓ Directories created
✓ Patient database loaded: 26 patients
✓ Vector database initialized: 20 documents
============================================================
System ready!
Server will start at: http://0.0.0.0:8000
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 8: Access the Application

Open your web browser and go to:
```
http://localhost:8000
```

You should see the Medical AI Assistant interface!

## First Time Usage

### Test the System

1. **Start a conversation**: Type "Hello, my name is John Smith"
2. **Wait for response**: The receptionist agent will retrieve the patient data
3. **View patient info**: Check the right panel for discharge information
4. **Ask a medical question**: Try "What are the side effects of my medications?"
5. **See clinical agent**: The system will switch to the clinical agent with RAG support

### Sample Patient Names to Try

- John Smith
- Maria Garcia
- Robert Johnson
- Sarah Chen
- James Wilson
- Lisa Thompson
- Michael Brown
- Emily Davis

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "GROQ_API_KEY not set"

**Solution**: 
1. Check `.env` file exists
2. Verify API key is correct
3. No spaces around the `=` sign
4. Restart the application

### Issue: "Port 8000 already in use"

**Solution**: Change port in `.env`:
```env
PORT=8001
```

### Issue: "Vector database initialization failed"

**Solution**: This is OK! The system will use fallback knowledge automatically.

### Issue: Browser shows "Connection refused"

**Solution**:
1. Check if server is running
2. Try `http://127.0.0.1:8000` instead
3. Check firewall settings

## Advanced Configuration

### Using a Custom PDF

1. Place your PDF in `data/` folder:
```bash
data/comprehensive-clinical-nephrology.pdf
```

2. Update `.env`:
```env
PDF_PATH=./data/your-custom-file.pdf
```

3. Delete existing vector store:
```bash
rmdir /s data\vector_store
```

4. Restart application - it will reprocess the PDF

### Adjusting RAG Parameters

In `.env`:
```env
CHUNK_SIZE=1000          # Size of text chunks
CHUNK_OVERLAP=200        # Overlap between chunks
TOP_K_RESULTS=3          # Number of results to retrieve
```

### Changing the LLM Model

In `.env`:
```env
GROQ_MODEL=llama-3.1-70b-versatile    # Default
# Or try:
# GROQ_MODEL=mixtral-8x7b-32768
# GROQ_MODEL=llama2-70b-4096
```

## Monitoring and Logs

### View Logs

```bash
# View all logs
type logs\system.log

# View last 20 lines
powershell -command "Get-Content logs\system.log -Tail 20"

# Follow logs in real-time
powershell -command "Get-Content logs\system.log -Wait"
```

### Check System Status

Visit: http://localhost:8000/api/status

Response:
```json
{
  "status": "operational",
  "patient_count": 26,
  "vector_db_documents": 20,
  "active_sessions": 1
}
```

## Stopping the Application

Press `Ctrl+C` in the terminal where the server is running.

## Updating the Application

1. Pull latest changes (if using git)
2. Update dependencies:
```bash
pip install -r requirements.txt --upgrade
```
3. Restart the application

## Getting Help

1. Check `README.md` for detailed documentation
2. Review `logs/system.log` for error details
3. Check the troubleshooting section above
4. Open an issue on GitHub (if applicable)

## Next Steps

- Explore the API endpoints at http://localhost:8000/docs
- Customize patient data in `data/patient_reports.json`
- Review the code in `backend/` folder
- Add your own medical knowledge PDF
- Integrate with your systems

---

**Congratulations! Your Medical AI Assistant is ready to use! 🎉**
