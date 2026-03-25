# Video UGC Pipeline

This project automates the creation of user-generated content (UGC) videos from campaign briefings using AI technology. The pipeline includes:
- Campaign management via REST API
- AI-powered prompt generation from briefings
- Video generation from prompts
- Automatic upload to Google Drive

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# LLM Configuration (Choose one)
GROK_API_KEY=your_grok_api_key_here           # For Grok API
# OR
HF_API_KEY=your_hf_api_key_here               # Hugging Face API key for free tier
HF_MODEL=meta-llama/Meta-Llama-3-8B-Instruct # Model to use
HF_INFERENCE_API_URL=https://huggingface.co   # For newer HF endpoints

# Video API Configuration
VIDEO_API_URL=https://your-video-api-url.com
VIDEO_API_KEY=your_video_api_key_here

# Google Drive Configuration
GOOGLE_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id

# Database Configuration (default uses local SQLite)
DATABASE_URL=sqlite:///./video_ugc_pipeline.db

# Timeouts and Retries
VIDEO_RENDER_TIMEOUT=600                      # 10 minutes timeout for video rendering
REQUEST_TIMEOUT=30                           # 30 seconds for API requests
MAX_RETRIES=3                                # Number of retries for failed requests
```

### 2. Running the Application

#### Option A: Direct Python Execution
```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy python-dotenv pydantic pydantic-settings requests huggingface_hub

# Run the application
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Using the Start Script
```bash
python start_app.py
```

### 3. API Endpoints

- `POST /api/campaigns/` - Create a new campaign
- `GET /api/campaigns/` - List all campaigns
- `GET /api/jobs/{job_id}` - Get details for a specific job

Example request to create a campaign:
```json
{
  "name": "Summer Sale Campaign",
  "briefing_text": "Create a promotional video for our summer sale featuring beach-themed visuals and upbeat music..."
}
```

### 4. How It Works

The pipeline follows this state machine:

1. **PENDING**: Campaign submitted, waiting for processing
2. **PROMPT_GENERATED**: AI has created a video prompt from the briefing
3. **PROCESSING_VIDEO**: Video is being generated from the prompt
4. **COMPLETED**: Video has been generated and uploaded to Google Drive
5. **FAILED/TIMEOUT/UPLOAD_FAILED**: Processing failed, timed out, or upload failed

### 5. Troubleshooting

- Make sure all required environment variables are set
- Check that the database is accessible
- Verify API keys and endpoints are correct
- Ensure the worker thread is running (it processes jobs automatically)
- Look for error messages in the application logs

### 6. Worker Process

The application automatically starts a background worker that:
- Checks for pending jobs
- Sends jobs through the state machine
- Polls external APIs for video processing status
- Uploads completed videos to Google Drive