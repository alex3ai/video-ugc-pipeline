"""
Startup script to run the Video UGC Pipeline application
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages if not already installed"""
    requirements = [
        "fastapi",
        "sqlalchemy", 
        "pydantic",
        "requests",
        "python-dotenv",
        "pydantic-settings",
        "uvicorn",
        "gradio-client",
        "moviepy",
        "huggingface_hub"
    ]
    
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
            print(f"✓ {req} already installed")
        except ImportError:
            print(f"Installing {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def main():
    print("Video UGC Pipeline Startup Script")
    print("="*40)
    
    # Install requirements
    install_requirements()
    
    # Check environment variables
    print("\nChecking environment variables:")
    env_vars = [
        ("HF_API_KEY", os.environ.get('HF_API_KEY')),
        ("HF_SPACE_MODEL", os.environ.get('HF_SPACE_MODEL', 'AlexMendes33/Wan-AI-Wan2.1-T2V-1.3B')),  # Updated to user's Space
        ("GOOGLE_CREDENTIALS_PATH", os.environ.get('GOOGLE_CREDENTIALS_PATH')),
        ("LLAMA_API_KEY or HF_API_KEY", os.environ.get('LLAMA_API_KEY') or os.environ.get('HF_API_KEY')),
        ("DATABASE_URL", os.environ.get('DATABASE_URL', 'sqlite:///./video_ugc_pipeline.db'))
    ]
    
    for name, value in env_vars:
        if value:
            print(f"✓ {name} is set")
        else:
            print(f"⚠ {name} is NOT set (this may cause issues)")
    
    # Import and test video connection
    print("\nTesting video provider connection...")
    try:
        from services.video_service.video_service import test_video_api_connection, validate_hf_repo_access
        from config import settings

        if validate_hf_repo_access(settings.HF_SPACE_MODEL):
            print("✓ Video provider repository is accessible")
            if test_video_api_connection():
                print("✓ Video provider connection successful")
            else:
                print("⚠ Video provider connection failed - please check your configuration")
        else:
            print("⚠ Video provider repository not accessible - please check your configuration and permissions")
    except ImportError as e:
        print(f"⚠ Could not test video provider: {e}")
    except Exception as e:
        print(f"⚠ Error testing video provider: {e}")
    
    print("\nStarting the application...")
    print("The application is now running. You can:")
    print("- Submit campaigns to /api/campaigns/")
    print("- List campaigns at /api/campaigns/")
    print("- Access the worker logs in the console")
    print("- Visit http://localhost:8000 for API documentation")
    print("- The system will now generate videos using your configured Hugging Face Space")
    
    # Start the application
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    main()