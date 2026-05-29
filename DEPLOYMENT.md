# 🚀 Deployment Guide

This guide covers deploying the Dataset Harmonization Platform to various cloud platforms and local environments.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
4. [Render.com Deployment](#rendercom-deployment)
5. [AWS EC2 Deployment](#aws-ec2-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

- Python 3.9+
- pip package manager
- Git (optional)

### Step 1: Clone/Setup Project

```bash
cd "path/to/Code (With frontend)"
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python database.py
```

### Step 5: Start Ollama (in separate terminal)

```bash
ollama run llama3
```

### Step 6: Run Application

```bash
# Option 1: Using startup script
# Windows
run.bat

# Linux/Mac
bash run.sh

# Option 2: Direct command
streamlit run app.py --server.port=8501
```

The app will be available at `http://localhost:8501`

---

## Docker Deployment

### Build Docker Image

```bash
docker build -t harmonization-app:latest .
```

### Run with Docker

```bash
# Windows
docker run -p 8501:8501 -v "%cd%\user_outputs:/app/user_outputs" -v "%cd%\app_database.db:/app/app_database.db" harmonization-app:latest

# Linux/Mac
docker run -p 8501:8501 -v $(pwd)/user_outputs:/app/user_outputs -v $(pwd)/app_database.db:/app/app_database.db harmonization-app:latest
```

### Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Rebuild services
docker-compose up -d --build
```

**Note**: Docker Compose will start both the app and Ollama service.

---

## Streamlit Cloud Deployment

### Prerequisites

- GitHub account
- Streamlit account (free at [streamlit.io/cloud](https://streamlit.io/cloud))

### Steps

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **Create Streamlit secrets file**
   - Create `.streamlit/secrets.toml` in your repository:
   ```toml
   [ollama]
   host = "http://your-ollama-server:11434"
   model = "llama3"
   ```

3. **Deploy on Streamlit Cloud**
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "Deploy an app"
   - Connect GitHub repository
   - Select branch: `main`
   - Set main file: `app.py`
   - Click "Deploy"

4. **Configure Advanced Settings**
   - Set Python version: 3.11
   - Add environment variables in "Advanced settings"

### Environment Variables to Set

```
OLLAMA_HOST=http://your-ollama-server:11434
ENVIRONMENT=production
DEBUG=false
```

**Important**: Streamlit Cloud doesn't have Ollama built-in. You need to either:
- Use an external Ollama server
- Use a cloud-hosted LLM API (OpenAI, Hugging Face, etc.)

---

## Render.com Deployment

### Prerequisites

- Render.com account (free tier available)
- GitHub repository with code

### Steps

1. **Connect GitHub to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub account
   - Select your repository

2. **Configure Service**
   - Name: `dataset-harmonization-app`
   - Environment: `Python 3.11`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`

3. **Set Environment Variables**
   ```
   ENVIRONMENT=production
   DEBUG=false
   OLLAMA_HOST=http://ollama-service:11434
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Using render.yaml

```bash
# Create render.yaml (already provided in repo)
# Push to GitHub
git add render.yaml
git commit -m "Add render deployment config"
git push

# Deploy via render.yaml
# Visit your Render dashboard and deploy
```

---

## AWS EC2 Deployment

### Prerequisites

- AWS account
- EC2 instance (t3.medium or larger recommended)
- Security group with ports 8501 and 11434 open

### Steps

1. **Connect to EC2 Instance**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

2. **Install Dependencies**
   ```bash
   # Update system
   sudo yum update -y
   sudo yum install -y python3 python3-pip git

   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

4. **Setup Application**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 database.py
   ```

5. **Start Ollama (in background)**
   ```bash
   nohup ollama serve &
   ollama run llama3
   ```

6. **Start Application (in background)**
   ```bash
   nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
   ```

7. **Access Application**
   ```
   http://your-instance-ip:8501
   ```

---

## Production Best Practices

### Security

1. **Use Environment Variables**
   - Never commit sensitive data
   - Use `.env` files (add to `.gitignore`)
   - Use platform-specific secrets management

2. **Enable HTTPS**
   - Use a reverse proxy (Nginx)
   - Obtain SSL certificate (Let's Encrypt)

3. **Database Security**
   - Use strong database passwords
   - Backup database regularly
   - Consider using managed database service

### Performance

1. **Caching**
   ```python
   @st.cache_data
   def load_data():
       return run_pipeline(files)
   ```

2. **Resource Limits**
   - Set max upload size: 100MB
   - Use streaming for large files
   - Implement rate limiting

3. **Monitoring**
   - Enable application logging
   - Set up error tracking (Sentry)
   - Monitor resource usage

### Scalability

1. **Load Balancing**
   - Use AWS ELB or similar
   - Deploy multiple instances
   - Use containerization (Docker)

2. **Database**
   - Use connection pooling
   - Implement caching layer (Redis)
   - Archive old records

---

## Configuration Files Reference

### .streamlit/config.toml

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "viewer"

[server]
maxUploadSize = 100
enableXsrfProtection = true
port = 8501
headless = true
```

### .env Example

```
ENVIRONMENT=production
DEBUG=false
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
MAX_UPLOAD_SIZE_MB=100
SESSION_TIMEOUT_MINUTES=60
```

---

## Monitoring and Maintenance

### Logs

```bash
# View Streamlit logs
tail -f ~/.streamlit/logs/app.log

# View Docker logs
docker logs -f harmonization-app

# View Docker Compose logs
docker-compose logs -f
```

### Database Backup

```bash
# SQLite backup
cp app_database.db app_database.backup.db

# Scheduled backup (Linux cron)
0 2 * * * cp /path/to/app_database.db /backup/app_database_$(date +\%Y\%m\%d).db
```

### Cleaning Up

```bash
# Remove old output files
find user_outputs/ -mtime +30 -delete

# Clear cache
rm -rf .streamlit/cache

# Remove Docker unused data
docker system prune -a
```

---

## Troubleshooting Deployment

### Application Won't Start

```bash
# Check Python version
python3 --version

# Check dependencies
pip list | grep streamlit

# Test imports
python3 -c "import streamlit; print(streamlit.__version__)"
```

### Database Lock Error

```bash
# Check if database is in use
lsof app_database.db

# Restart application
pkill -f streamlit
streamlit run app.py
```

### Ollama Connection Error

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check network connectivity
ping ollama-host

# Restart Ollama
pkill ollama
ollama serve
```

### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>

# Use different port
streamlit run app.py --server.port=8502
```

---

## Support and Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Render Docs**: https://render.com/docs
- **Docker Docs**: https://docs.docker.com
- **Ollama Docs**: https://github.com/ollama/ollama

For issues:
1. Check application logs
2. Review troubleshooting section
3. Check platform-specific documentation
4. Contact support with error details

---

Last Updated: May 27, 2026
