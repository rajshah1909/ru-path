# How to Run RU-PATH Parking Chatbot

## Prerequisites

1. **Python 3.9+** (you have Python 3.9.2)
2. **Virtual Environment** (optional but recommended)
3. **Environment Variables** (for DeepSeek API)

## Setup Steps

### 1. Activate Virtual Environment (if using one)

On Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Or on Windows Command Prompt:
```cmd
venv\Scripts\activate.bat
```

### 2. Install Dependencies (if not already installed)

```powershell
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root with your DeepSeek API key:

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
PORT=5000
ENVIRONMENT=development
FLASK_SECRET_KEY=your-secret-key-here
```

**Note**: Replace `your_api_key_here` with your actual DeepSeek API key.

## Running the Application

### Option 1: Run directly with Python

```powershell
python app.py
```

### Option 2: Run with Flask (if flask command is available)

```powershell
flask run
```

### Option 3: Run with specific port

```powershell
$env:PORT=5000; python app.py
```

## Accessing the Application

Once running, the API will be available at:
- **Local**: http://localhost:5000
- **Network**: http://0.0.0.0:5000

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/chat` - Chat with the chatbot
- `POST /api/reset` - Reset conversation
- `GET /api/lots` - Get parking lots
- `GET /api/stats` - Get statistics

## Testing the API

You can test the API using:

```powershell
# Health check
curl http://localhost:5000/health

# Chat endpoint
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d '{\"message\": \"Where can I park on Busch campus?\"}'
```

Or use the test files:
```powershell
python test_api.py
python test_chatbot.py
```

## Troubleshooting

1. **Import errors**: Make sure you're in the project directory and have activated the virtual environment
2. **API key errors**: Check that your `.env` file exists and contains `DEEPSEEK_API_KEY`
3. **JSON file not found**: Ensure `rupath_parking_base.json` is in the project root directory
4. **Port already in use**: Change the PORT in `.env` or kill the process using port 5000


