# 🔧 Troubleshooting Guide

Common issues and their solutions for the Dataset Harmonization Platform.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Ollama Connection](#ollama-connection)
4. [Database Issues](#database-issues)
5. [Performance Problems](#performance-problems)
6. [Streamlit Issues](#streamlit-issues)
7. [Deployment Issues](#deployment-issues)

---

## Installation Issues

### Python Not Found

**Error**: `python: command not found` or `python is not recognized`

**Solution**:
- Install Python 3.9+ from [python.org](https://www.python.org)
- On Windows, check "Add Python to PATH" during installation
- Verify installation:
  ```bash
  python --version
  # or
  python3 --version
  ```

### pip Command Not Found

**Error**: `pip: command not found`

**Solution**:
```bash
# Use pip module directly
python -m pip install -r requirements.txt

# Or update pip
python -m pip install --upgrade pip
```

### Permission Denied

**Error**: `Permission denied` when creating venv or installing packages

**Solution - Windows**:
- Run Command Prompt as Administrator
- Try using `python -m venv venv` instead of `virtualenv venv`

**Solution - Linux/Mac**:
```bash
# Add --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Activate virtual environment first
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Then install
pip install -r requirements.txt
```

---

## Runtime Errors

### Database File Locked

**Error**: `database is locked`

**Solution**:
1. Close all Streamlit instances:
   ```bash
   # Windows
   taskkill /f /im streamlit.exe
   
   # Linux/Mac
   pkill -f streamlit
   ```

2. Reinitialize database:
   ```bash
   python database.py
   ```

3. Restart application

### File Not Found Error

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`

**Solution**:
- Ensure you're running from the correct directory:
  ```bash
  cd "path/to/Code (With frontend)"
  ```

- Verify template files exist:
  ```bash
  ls templates/
  # Should contain: canonical_template.json, ignore_columns.json, rule_based_mapping.json
  ```

### Memory Error

**Error**: `MemoryError` or out of memory

**Solution**:
- Use smaller datasets first
- Clear cache:
  ```bash
  rm -rf .streamlit/cache
  ```
- Increase available memory
- Close other applications

### CSV Parsing Error

**Error**: `ParserError` or `Error tokenizing data`

**Solution**:
- Ensure CSV is properly formatted
- Check for encoding issues:
  ```python
  df = pd.read_csv('file.csv', encoding='utf-8')
  # or
  df = pd.read_csv('file.csv', encoding='latin1')
  ```
- Remove any special characters from first row
- Verify file is actually CSV format

---

## Ollama Connection

### Ollama Not Running

**Error**: `Connection refused` or `Cannot connect to Ollama`

**Solution**:
1. Check if Ollama is installed:
   ```bash
   ollama version
   ```

2. Start Ollama:
   ```bash
   ollama serve
   # In another terminal
   ollama run llama3
   ```

3. Verify connection:
   ```bash
   curl http://127.0.0.1:11434/api/tags
   ```

### Model Not Found

**Error**: `Error: model not found` or `Ollama model unavailable`

**Solution**:
1. Pull the model:
   ```bash
   ollama pull llama3
   ```

2. Verify model is installed:
   ```bash
   ollama list
   ```

3. Update application config if using different model:
   ```python
   # In semantic_mapping.py
   "model": "your-model-name"
   ```

### Timeout Error

**Error**: `Request timeout` or `Ollama request timed out`

**Solution**:
- Increase timeout in `semantic_mapping.py`:
  ```python
  response = requests.post(url, json=payload, timeout=60)  # Increase from 30 to 60
  ```

- Ensure Ollama has sufficient resources
- Use a smaller model if available
- Check network connection

### Port Already in Use

**Error**: `Address already in use` for port 11434

**Solution - Windows**:
```cmd
netstat -ano | findstr :11434
taskkill /PID <PID> /F
```

**Solution - Linux/Mac**:
```bash
lsof -i :11434
kill -9 <PID>
```

### Windows Localhost Issues

**Error**: `Cannot connect to localhost or 127.0.0.1`

**Solution**:
- Try using IP address explicitly:
  ```python
  url = "http://127.0.0.1:11434/api/generate"  # Instead of localhost
  ```

- Check Windows firewall:
  1. Open "Windows Defender Firewall with Advanced Security"
  2. Add inbound rule for port 11434

---

## Database Issues

### Corrupted Database

**Error**: `database disk image malformed`

**Solution**:
1. Backup existing database:
   ```bash
   copy app_database.db app_database.backup.db
   ```

2. Delete corrupted database:
   ```bash
   rm app_database.db
   ```

3. Reinitialize:
   ```bash
   python database.py
   ```

### Lost User Data

**Error**: Users or history not showing up

**Solution**:
1. Check database integrity:
   ```bash
   sqlite3 app_database.db ".tables"
   ```

2. Query users:
   ```bash
   sqlite3 app_database.db "SELECT COUNT(*) FROM users;"
   ```

3. Restore from backup if available

### Disk Space Full

**Error**: `No space left on device` or `Disk quota exceeded`

**Solution**:
- Check disk space:
  ```bash
  # Windows
  dir C:\
  
  # Linux
  df -h
  ```

- Clean old files:
  ```bash
  rm -rf user_outputs/*_old
  find . -name "*.log" -delete
  ```

- Compress/archive old data

---

## Performance Problems

### Slow Upload Processing

**Issue**: Taking too long to process files

**Solution**:
- Start with smaller files (< 10MB)
- Check system resources:
  ```bash
  # Windows - Task Manager or
  wmic os get totalvisiblememorsize,freephysicalmemory
  
  # Linux
  free -h
  ```

- Increase Ollama timeout
- Use faster hardware

### Slow Harmonization

**Issue**: Harmonization job is slow

**Solution**:
- Optimize Ollama model:
  ```bash
  ollama pull llama3:7b  # Smaller model
  ```

- Check number of columns in dataset
- Reduce sample rows for matching
- Enable caching

### High Memory Usage

**Issue**: Memory usage grows continuously

**Solution**:
- Clear Streamlit cache:
  ```bash
  rm -rf .streamlit/cache
  ```

- Restart application regularly
- Process files in batches
- Use dataset streaming

---

## Streamlit Issues

### Streamlit Port Already in Use

**Error**: `Streamlit cannot bind to port 8501`

**Solution**:
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8501
kill -9 <PID>

# Use different port
streamlit run app.py --server.port=8502
```

### Streamlit Not Starting

**Error**: App doesn't start or freezes

**Solution**:
1. Clear Streamlit cache and config:
   ```bash
   rm -rf ~/.streamlit
   ```

2. Verify Streamlit installation:
   ```bash
   pip install --upgrade streamlit
   ```

3. Run with debug:
   ```bash
   streamlit run app.py --logger.level=debug
   ```

### Session State Issues

**Error**: User data not persisting or sessions resetting

**Solution**:
- Clear browser cache
- Disable browser cache clearing on exit
- Check browser privacy settings
- Use incognito/private mode for testing

### File Upload Not Working

**Error**: Cannot upload files

**Solution**:
1. Check file size (max 100MB default):
   ```python
   # In .streamlit/config.toml
   [server]
   maxUploadSize = 200  # Increase to 200MB
   ```

2. Verify file format is CSV
3. Check file permissions
4. Try different file
5. Clear browser cache

---

## Deployment Issues

### Docker Build Failed

**Error**: `failed to build image`

**Solution**:
```bash
# Remove old images
docker rmi harmonization-app:latest

# Build with no cache
docker build --no-cache -t harmonization-app:latest .

# Check Docker resources
docker system df
```

### Docker Run Error

**Error**: `container exited with error`

**Solution**:
```bash
# Check logs
docker logs <container_id>

# Run with interactive terminal
docker run -it harmonization-app:latest

# Check if ports are available
docker port <container_id>
```

### Streamlit Cloud Deployment Failed

**Error**: Build or deployment fails on Streamlit Cloud

**Solution**:
1. Check `requirements.txt` for compatibility
2. Verify GitHub repository structure
3. Check logs in Streamlit Cloud dashboard
4. Try smaller requirements first
5. Contact Streamlit support

### Render Deployment Failed

**Error**: Deployment fails on Render

**Solution**:
1. Check build logs in Render dashboard
2. Verify `render.yaml` syntax
3. Ensure environment variables are set
4. Check Python version compatibility
5. Verify start command is correct

---

## Getting Help

### Debug Mode

Enable debug logging:

```bash
# Streamlit
streamlit run app.py --logger.level=debug

# Python
export PYTHONVERBOSE=1
python app.py
```

### Log Files

Check application logs:

```bash
# Streamlit logs
cat ~/.streamlit/logs/streamlit.log

# Application logs
tail -f app.log
```

### Collect Debug Info

```bash
# System info
python -c "import platform; print(platform.platform())"
python -c "import sys; print(sys.version)"

# Dependency versions
pip list

# Ollama status
curl -v http://127.0.0.1:11434/api/tags
```

### Report Issues

When reporting issues, provide:
- Error message (full)
- Steps to reproduce
- System information (OS, Python version)
- Relevant log files
- Screenshots if applicable
- Output of debug info commands above

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Virtual env not active | `source venv/bin/activate` or `venv\Scripts\activate` |
| Install dependencies | `pip install -r requirements.txt` |
| Start application | `streamlit run app.py` |
| Initialize database | `python database.py` |
| Start Ollama | `ollama serve` |
| Test Ollama | `curl http://127.0.0.1:11434/api/tags` |
| Clear cache | `rm -rf .streamlit/cache` |
| Check running processes | `ps aux \| grep streamlit` |
| Kill process | `pkill -f streamlit` |
| Docker rebuild | `docker build --no-cache -t harmonization-app . ` |

---

## Additional Resources

- **Python Documentation**: https://docs.python.org
- **Streamlit Docs**: https://docs.streamlit.io
- **Ollama Documentation**: https://github.com/ollama/ollama
- **Pandas Documentation**: https://pandas.pydata.org/docs
- **SQLite Documentation**: https://www.sqlite.org/docs.html

## Still Having Issues?

1. Review this guide completely
2. Check application logs
3. Search for similar issues online
4. Check GitHub issues
5. Contact support with debug information

---

Last Updated: May 27, 2026
Version: 1.0.0
