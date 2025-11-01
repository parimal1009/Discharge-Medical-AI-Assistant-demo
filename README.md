# Post Discharge Medical AI Assistant

A production-ready multi-agent AI system for post-discharge patient care with RAG (Retrieval-Augmented Generation) capabilities.

## 🌟 Features

✅ **Multi-Agent Architecture** - Receptionist and Clinical agents with intelligent routing  
✅ **RAG Implementation** - Semantic search over nephrology knowledge base  
✅ **Web Search Integration** - Current medical information retrieval  
✅ **Patient Database** - 25+ sample discharge reports  
✅ **Comprehensive Logging** - Full system interaction tracking  
✅ **Medical Safety** - Appropriate disclaimers and limitations  
✅ **Professional UI** - Clean, responsive web interface  

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- API Keys:
  - Groq API (required) - Get from https://console.groq.com
  - Tavily API (optional) - Get from https://tavily.com

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
```

### 3. Run the Application

```bash
python run.py
```

The application will:
- Create necessary directories
- Initialize patient database with 25+ samples
- Process PDF and create vector embeddings (or use fallback knowledge)
- Start the web server

Access at: **http://localhost:8000**

## 📁 Project Structure

```
DATASMITH/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── agents/
│   │   └── orchestrator.py     # Multi-agent orchestration
│   ├── database/
│   │   ├── patient_db.py       # Patient data management
│   │   └── vector_db.py        # Vector database & RAG
│   ├── tools/
│   │   ├── patient_retrieval.py
│   │   └── web_search_tool.py
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── utils/
│       └── logger.py           # Logging system
├── frontend/
│   └── templates/
│       └── index.html          # Web interface
├── data/
│   ├── patient_reports.json    # Patient database (auto-generated)
│   └── vector_store/           # Vector embeddings (auto-generated)
├── logs/
│   └── system.log              # System logs (auto-generated)
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

## 💡 Usage Guide

### Starting a Conversation

1. **Open the Application**: Navigate to http://localhost:8000
2. **Provide Your Name**: The receptionist agent will ask for your full name
3. **Get Your Report**: Your discharge information will be retrieved automatically
4. **Ask Questions**: Medical queries are routed to the clinical agent with RAG support

### Example Interactions

**Receptionist Agent:**
- "Hello, my name is John Smith"
- "I need my discharge information"
- "When is my follow-up appointment?"

**Clinical Agent:**
- "What are the side effects of Lisinopril?"
- "Can you explain my kidney disease stage?"
- "What dietary changes should I make?"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | - | Yes |
| `TAVILY_API_KEY` | Tavily API key for web search | - | No |
| `GROQ_MODEL` | LLM model name | llama-3.1-70b-versatile | No |
| `EMBEDDINGS_MODEL` | Sentence transformer model | all-MiniLM-L6-v2 | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `CHUNK_SIZE` | Text chunk size for RAG | 1000 | No |
| `TOP_K_RESULTS` | Number of RAG results | 3 | No |

### Customizing Patient Data

Edit `data/patient_reports.json` to add or modify patient records:

```json
{
  "patient_name": "Jane Doe",
  "discharge_date": "2024-03-15",
  "primary_diagnosis": "Acute Kidney Injury",
  "medications": ["Medication 1", "Medication 2"],
  "dietary_restrictions": "Low sodium diet",
  "follow_up": "Nephrology in 1 week",
  "warning_signs": "Decreased urine output, swelling",
  "discharge_instructions": "Monitor symptoms daily"
}
```

## 🔌 API Endpoints

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, my name is John Smith",
  "session_id": "session_123",
  "patient_name": "John Smith"
}
```

### Get Patient
```http
GET /api/patient/{patient_name}
```

### System Status
```http
GET /api/status
```

### View Logs
```http
GET /api/logs
```

## 🧪 Testing

### Manual Testing

1. Start the application
2. Open http://localhost:8000
3. Test receptionist flow:
   - Provide patient name
   - Verify discharge report retrieval
4. Test clinical flow:
   - Ask medical questions
   - Verify RAG context usage
   - Check source citations

### API Testing

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, my name is John Smith",
    "session_id": "test_session",
    "patient_name": null
  }'

# Test system status
curl http://localhost:8000/api/status
```

## 📊 System Architecture

### Multi-Agent Flow

```
User Message
    ↓
Receptionist Agent
    ├─→ Patient Retrieval Tool
    └─→ Detect Medical Query
            ↓
    Clinical Agent
        ├─→ RAG Search (Vector DB)
        ├─→ Web Search Tool (Optional)
        └─→ Generate Response
```

### RAG Pipeline

```
Query → Embedding → Vector Search → Top-K Results → Context → LLM → Response
```

## ⚠️ Medical Disclaimer

**IMPORTANT**: This AI assistant is for **educational purposes only**. It should NOT be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

## 🐛 Troubleshooting

### Common Issues

**Issue**: "GROQ_API_KEY not found"
- **Solution**: Ensure `.env` file exists with valid API key

**Issue**: "Vector database initialization failed"
- **Solution**: System will use fallback knowledge base automatically

**Issue**: "Patient not found"
- **Solution**: Check spelling or use last name only

**Issue**: Port 8000 already in use
- **Solution**: Change `PORT` in `.env` file

### Logs

Check `logs/system.log` for detailed system information:

```bash
# View recent logs
tail -f logs/system.log

# Search for errors
grep ERROR logs/system.log
```

## 🔒 Security Considerations

- API keys stored in `.env` (not committed to git)
- Patient data stored locally
- No external data transmission except API calls
- Session data cleared on server restart

## 🚀 Deployment

### Production Checklist

- [ ] Set `RELOAD=False` in `.env`
- [ ] Configure proper `HOST` and `PORT`
- [ ] Set up reverse proxy (nginx/Apache)
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Implement authentication
- [ ] Regular security updates

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- Check the troubleshooting section
- Review system logs
- Open an issue on GitHub

## 🎯 Future Enhancements

- [ ] User authentication system
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Mobile app
- [ ] Integration with EHR systems
- [ ] Advanced analytics dashboard
- [ ] Appointment scheduling
- [ ] Medication reminders

## 📚 References

- LangChain Documentation: https://python.langchain.com
- FastAPI Documentation: https://fastapi.tiangolo.com
- ChromaDB Documentation: https://docs.trychroma.com
- Groq API: https://console.groq.com

---

**Built with ❤️ for better post-discharge patient care**
