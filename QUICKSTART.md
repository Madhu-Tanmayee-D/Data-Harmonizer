# 🎯 Quick Start Guide

Get the Dataset Harmonization Platform running in 5 minutes!

## 📋 Prerequisites

- Python 3.9 or higher
- Ollama (for LLM-based semantic mapping)
- 4GB RAM minimum
- 500MB disk space

## ⚡ Quick Start (Windows)

### 1. Download and Install Ollama

1. Go to [ollama.ai](https://ollama.ai)
2. Download the Windows installer
3. Install and run Ollama
4. Open a terminal and run:
   ```bash
   ollama pull llama3
   ```

### 2. Setup Application

Open Command Prompt and run:

```bash
# Navigate to project directory
cd "path\to\Code (With frontend)"

# Run the startup script
run.bat
```

That's it! The app will open at `http://localhost:8501`

## 🐧 Quick Start (Linux/Mac)

### 1. Install Ollama

```bash
# On Mac
brew install ollama

# On Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3
```

### 2. Setup Application

```bash
# Navigate to project directory
cd "path/to/Code (With frontend)"

# Make script executable
chmod +x run.sh

# Run the startup script
./run.sh
```

App will be available at `http://localhost:8501`

## 🎨 Using the Application

### Step 1: Create Account
- Click "Sign Up"
- Enter username, email, and password
- Click "Sign Up"

### Step 2: Upload Datasets
- Click "Dashboard" 
- Upload two CSV files
- Preview the data

### Step 3: Start Harmonization
- Click "🔄 Start Harmonization"
- Wait for processing to complete
- View the harmonized dataset

### Step 4: Download Results
- Click "📥 Download Harmonized Dataset"
- File will download as CSV

### Step 5: View History
- Click "📜 History" in sidebar
- See all uploads, processing jobs, and downloads

## 📁 Project Structure

```
Code (With frontend)/
├── app.py                  # Main Streamlit app
├── auth.py                 # User authentication
├── database.py             # Database setup
├── db_utils.py             # Database operations
├── config.py               # Configuration
├── utils.py                # Helper functions
├── pipeline.py             # Data processing
├── requirements.txt        # Dependencies
├── run.bat / run.sh        # Startup scripts
├── Dockerfile              # Docker config
├── docker-compose.yml      # Docker Compose config
├── .streamlit/config.toml  # Streamlit config
└── README.md               # Full documentation
```

## 🔧 Common Commands

```bash
# Start application
streamlit run app.py

# Run tests
pytest test_app.py -v

# Initialize database
python database.py

# Check configuration
python config.py

# Start with Docker
docker-compose up

# Stop Docker services
docker-compose down
```

## 🐛 Troubleshooting

### Ollama not connecting?
```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama
ollama serve
```

### Database locked?
```bash
# Reinitialize database
python database.py
```

### Port 8501 in use?
```bash
# Use different port
streamlit run app.py --server.port=8502
```

## 📚 Documentation

- **README.md**: Full feature documentation
- **DEPLOYMENT.md**: Cloud deployment guides
- **TROUBLESHOOTING.md**: Common issues and solutions
- **API.md**: Complete API reference
- **test_app.py**: Unit tests

## 🚀 Next Steps

1. ✅ Start the application
2. ✅ Create a user account
3. ✅ Upload and harmonize datasets
4. ✅ Download results
5. 📖 Read full documentation for advanced features

## 💡 Tips

- Use datasets with similar structure for best results
- Start with smaller files (< 10MB) for testing
- Ensure Ollama is running before starting the app
- Check browser console for debugging (F12)
- Clear cache if experiencing issues: `rm -rf .streamlit/cache`

## 📞 Support

**Got issues?** Check these in order:

1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment issues  
3. [API.md](API.md) - API questions
4. Application logs in terminal

## 🎓 Learning Resources

- **Streamlit**: https://docs.streamlit.io
- **Pandas**: https://pandas.pydata.org
- **Ollama**: https://github.com/ollama/ollama
- **Python**: https://docs.python.org

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.9 | 3.11+ |
| RAM | 4 GB | 8+ GB |
| Disk | 500 MB | 2+ GB |
| CPU | 2 cores | 4+ cores |

## 🔐 Security Notes

- Passwords are hashed with PBKDF2-SHA256
- Database uses SQLite with foreign keys
- Consider using environment variables for secrets
- Use HTTPS in production
- Back up database regularly

## 🎉 You're All Set!

The application is now ready to use. Start harmonizing datasets!

**Need help?**
1. Check TROUBLESHOOTING.md
2. Review application logs
3. Read full documentation in README.md

---

**Happy Harmonizing! 🚀**

Last Updated: May 27, 2026
Version: 1.0.0
