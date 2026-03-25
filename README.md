# Video UGC Pipeline

## Overview
This project automates the creation of user-generated content (UGC) videos for marketing campaigns using AI. It leverages LLMs and text-to-video synthesis to create engaging video content from textual prompts.

## Features
- AI-powered campaign brief generation
- Automatic video script creation
- Text-to-video synthesis using free Hugging Face Spaces
- Video concatenation with smooth transitions
- Integration with Google Drive for asset storage

## Dependencies Installation

To run this project, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Hugging Face Setup

For the text-to-video generation, we use free Hugging Face Spaces. You'll need to:

1. Create an account on [Hugging Face](https://huggingface.co/)
2. Use the Wan2.1-T2V-1.3B model (or configure another in settings)
3. Make sure to accept the license for the model you choose

## Configuration

Create a `.env` file in the project root with the following variables:

```env
HF_API_KEY=your_huggingface_api_key
GOOGLE_CREDENTIALS_PATH=path_to_your_google_credentials_json
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
HF_SPACE_MODEL=Wan-AI/Wan2.1-T2V-1.3B
VIDEO_DURATION_PER_SEGMENT=5
CROSSFADE_DURATION=1.0
```

## Usage

Run the main application:

```bash
python main.py
```

Or run individual components for testing:

```bash
python test_services.py
python test_api.py
python test_e2e.py
python test_state_machine.py
```

## Architecture

The pipeline consists of the following components:

- **LLM Service**: Generates campaign briefs and video scripts using either Grok or Llama 3
- **Video Service**: Creates videos from text prompts using Hugging Face Spaces
- **Drive Service**: Uploads generated assets to Google Drive
- **Job Service**: Orchestrates the entire pipeline workflow

## New Video Generation Approach

Our video generation now follows this approach:

1. Uses the `gradio_client` library to connect to a free Text-to-Video Space on Hugging Face
2. Makes two sequential calls of 5 seconds each using the same prompt to extend video length
3. Uses `moviepy` to:
   - Load the two generated files
   - Apply a 1-second crossfade transition between them for smooth blending
   - Export the final 10-second video as `video_final_10s.mp4`
4. Includes error handling for Hugging Face queues or connection failures

## Testing

The project includes comprehensive tests for different aspects:

- `test_services.py`: Tests individual service functionalities (LLM, Video, Drive services)
- `test_api.py`: Tests API endpoints functionality
- `test_e2e.py`: End-to-end tests covering the complete pipeline flow
- `test_state_machine.py`: Tests the job status state machine transitions

## Error Handling

The system includes robust error handling for:
- Connection issues with Hugging Face Spaces
- Model queue backlogs
- File processing errors
- Google Drive upload failures

## Contributing

See `AGENTS.md` for detailed information about the agent architecture and contribution guidelines.

## Project Documentation

The project documentation is organized under the [.ai/docs/](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs) directory:
- [00_project-description.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/00_project-description.md) - Overall project description
- [01_user-stories.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/01_user-stories.md) - User stories and requirements
- [02_database-structure.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/02_database-structure.md) - Database structure and models
- [03_project-phases.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/03_project-phases.md) - Project phases and milestones
- [04_video-generation-setup.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/04_video-generation-setup.md) - Video generation setup and configuration
- [05_connector-errors.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/05_connector-errors.md) - Common errors and solutions
- [debugging_summary.md](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.ai/docs/debugging_summary.md) - Debugging information and lessons learned