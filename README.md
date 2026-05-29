# 🔄 Dataset Harmonization Platform

A comprehensive web-based platform for automated dataset harmonization and semantic column mapping using machine learning and natural language processing.

## 📋 Features

- **User Authentication**: Secure login/signup system with SQLite database
- **Dataset Upload**: Upload two CSV datasets for harmonization
- **Semantic Mapping**: Intelligent column mapping using LLM (Ollama/Llama3)
- **Data Harmonization**: Automatic standardization and unification of datasets
- **Processing History**: Track all uploads, processing jobs, and downloads
- **Download Results**: Export harmonized datasets as CSV
- **User Dashboard**: Comprehensive interface for all operations

## 🛠️ Technology Stack

### Frontend
- **Streamlit**: Interactive web interface
- **Plotly**: Data visualization

### Backend
- **Python**: Core backend logic
- **Pandas**: Data manipulation and processing
- **NumPy**: Numerical computations

### ML/NLP
- **Sentence Transformers**: Semantic similarity matching
- **Hugging Face**: Pre-trained models
- **PyTorch**: Deep learning framework
- **scikit-learn**: Machine learning utilities
- **Ollama**: Local LLM inference (Llama3)

### Database
- **SQLite**: User credentials and history storage

### Deployment
- **Streamlit Cloud**: For quick cloud deployment
- **Render.com**: For production deployments
- **Docker**: Containerization (optional)

## 📦 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Ollama with Llama3 model (for semantic mapping)
- 4GB+ RAM
- 500MB+ disk space

## 🚀 Quick Start

### 1. Clone or Setup Project

```bash
cd "path/to/Code (With frontend)"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python database.py
```

This will create `app_database.db` with all necessary tables.

### 4. Start Ollama (for LLM features)

In a separate terminal:

```bash
ollama run llama3
```

Make sure Ollama is running on `http://127.0.0.1:11434`

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### 6. Create an Account and Test

1. Sign up with a new account
2. Upload two CSV files
3. Click "Start Harmonization"
4. View and download results
5. Check history for previous jobs

## 📁 Project Structure

```
Code (With frontend)/
├── app.py                           # Main Streamlit application
├── database.py                      # Database initialization
├── auth.py                          # Authentication module
├── db_utils.py                      # Database utilities
├── pipeline.py                      # Data processing pipeline
├── semantic_mapping.py              # LLM-based column mapping
├── harmonization.py                 # Harmonization logic
├── preprocessing.py                 # Data preprocessing
├── dataset_loader.py                # Dataset loading utilities
├── schema_generator.py              # Schema generation
├── validation.py                    # Data validation
├── benchmark_evaluation.py          # Evaluation metrics
├── column_semantics.py              # Column semantics analysis
├── csvtoxlsx.py                     # CSV to XLSX conversion
├── requirements.txt                 # Python dependencies
├── setup.py                         # Setup configuration
├── render.yaml                      # Render.com deployment config
├── app_database.db                  # SQLite database (auto-created)
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── templates/
│   ├── canonical_template.json     # Target schema
│   ├── ignore_columns.json         # Columns to ignore
│   └── rule_based_mapping.json     # Mapping rules
├── outputs/                         # Processed outputs directory
└── user_outputs/                    # User-specific outputs directory
```

## 🔐 Security Features

- **Password Hashing**: PBKDF2-SHA256 with salt
- **Session Management**: Streamlit session state
- **Database Integrity**: Foreign key constraints
- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Graceful error handling with user feedback

## 📊 Database Schema

### Users Table
- Stores user credentials (hashed passwords)
- Tracks account creation and last login

### Upload History
- Records all file uploads with metadata
- Linked to user accounts

### Processing History
- Tracks harmonization jobs
- Stores job status and timestamps

### Download History
- Records downloaded files
- Links to processing jobs

## 🚢 Deployment

### Streamlit Cloud Deployment

1. Push code to GitHub
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub repository
4. Deploy with automatic environment setup

**Note**: You'll need to configure Ollama as an external service or use an API-based LLM service.

### Render.com Deployment

1. Create `render.yaml` (already provided)
2. Push to GitHub
3. Connect repository to Render
4. Deploy using provided configuration

**Environment Variables to Set**:
```
OLLAMA_HOST=http://your-ollama-server:11434
STREAMLIT_SERVER_PORT=10000
```

### Local Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t harmonization-app .
docker run -p 8501:8501 harmonization-app
```

## 🔧 Configuration

### Streamlit Settings (`.streamlit/config.toml`)
- Customize colors, fonts, and themes
- Adjust upload size limits
- Configure security settings

### Database Location
By default, SQLite database is stored at `app_database.db` in the project root.

### Ollama Configuration
Modify the Ollama URL in `semantic_mapping.py`:
```python
url = "http://127.0.0.1:11434/api/generate"
```

## 📝 Usage Guide

### Step 1: Register/Login
- Create a new account with username, email, and password
- Or login with existing credentials
- Credentials are securely hashed and stored

### Step 2: Upload Datasets
- Select two CSV files to harmonize
- Preview data before processing
- Check file size and structure

### Step 3: Start Harmonization
- Click "Start Harmonization" button
- System processes and maps columns semantically
- Progress is displayed in real-time

### Step 4: Download Results
- View harmonized dataset preview
- Download as CSV file
- Results stored in `user_outputs/` directory

### Step 5: View History
- Access upload history
- Track processing jobs
- Review download history

## 🐛 Troubleshooting

### Ollama Connection Error
```
ERROR: Ollama connection error
```
**Solution**: 
- Ensure Ollama is running: `ollama run llama3`
- Check if Ollama is accessible at `http://127.0.0.1:11434`
- Windows users may need to use `localhost` instead of `127.0.0.1`

### Database Lock Error
```
ERROR: database is locked
```
**Solution**:
- Close all other connections to the database
- Delete `app_database.db` and reinitialize: `python database.py`

### Out of Memory
**Solution**:
- Reduce dataset size
- Split large files into smaller chunks
- Increase system RAM

### Streamlit Session Timeout
**Solution**:
- Clear browser cache
- Restart Streamlit: `streamlit run app.py`

## 📈 Performance Optimization

- **Caching**: Streamlit caches data loading automatically
- **Batch Processing**: Process datasets in batches
- **Model Optimization**: Use quantized Ollama models
- **Database Indexing**: Indexes on user_id and timestamps

## 📚 API Reference

### Authentication Functions
```python
register_user(username, email, password)
login_user(username, password)
get_user_info(user_id)
```

### Database Functions
```python
save_upload_record(user_id, filename, file_path, file_size)
save_processing_record(user_id, upload_id_1, upload_id_2)
get_user_processing_history(user_id)
get_user_download_history(user_id)
```

### Pipeline Functions
```python
run_pipeline(uploaded_files)
semantic_column_mapping(dataset_columns, template_columns, sample_rows)
harmonize_dataset(dataframe, mapping)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review application logs
3. Contact: your-email@example.com

## 🎯 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced data validation rules
- [ ] Custom mapping rules editor
- [ ] Data quality scoring
- [ ] Batch processing API
- [ ] Real-time collaboration
- [ ] Advanced analytics and reporting
- [ ] Integration with cloud storage (AWS S3, Azure Blob)
- [ ] Docker support
- [ ] Mobile app

## 📊 Performance Metrics

- **Average Processing Time**: 5-30 seconds (depending on dataset size)
- **Memory Usage**: ~500MB base + dataset size
- **Database Size**: ~1MB per 1000 user records
- **Concurrent Users**: 100+ (with sufficient infrastructure)

## 🔄 Updates

Version: 1.0.0
Last Updated: May 27, 2026

---

**Happy Harmonizing! 🚀**
