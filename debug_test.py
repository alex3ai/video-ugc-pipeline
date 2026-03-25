"""
Debug script to test the basic functionality of the API and database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from models.entities import Campaign, PipelineJob, JobStatusEnum
from services.job_service.job_service import initialize_new_job
from config import settings

def test_basic_functionality():
    print("Testing basic functionality...")
    
    # Test database connection
    try:
        db = SessionLocal()
        print("✓ Database connection successful")
        
        # Test creating a campaign
        test_campaign = Campaign(
            name="Test Campaign",
            briefing_text="This is a valid briefing text with more than fifty characters to meet the minimum requirement."
        )
        
        db.add(test_campaign)
        db.commit()
        db.refresh(test_campaign)
        
        print(f"✓ Campaign created successfully with ID: {test_campaign.id}")
        
        # Test initializing a job
        job = initialize_new_job(db, test_campaign.id)
        print(f"✓ Job initialized successfully with ID: {job.id}, Status: {job.status.value}")
        
        # Clean up
        db.delete(job)
        db.delete(test_campaign)
        db.commit()
        print("✓ Cleanup successful")
        
    except Exception as e:
        print(f"✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_environment():
    print("\nChecking environment variables...")
    
    checks = [
        ("VIDEO_API_KEY", settings.VIDEO_API_KEY),
        ("GOOGLE_CREDENTIALS_PATH", settings.GOOGLE_CREDENTIALS_PATH),
        ("DATABASE_URL", settings.DATABASE_URL),
        ("LLAMA_API_KEY or HF_API_KEY", settings.LLAMA_API_KEY or settings.HF_API_KEY)
    ]
    
    for name, value in checks:
        if value:
            print(f"✓ {name} is set")
        else:
            print(f"✗ {name} is NOT set")

if __name__ == "__main__":
    check_environment()
    test_basic_functionality()