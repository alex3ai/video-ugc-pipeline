"""
Demo script for the Video UGC Pipeline

This script demonstrates the complete functionality of the pipeline:
1. Creates a campaign
2. Processes it through the state machine
3. Shows how the worker processes jobs
"""

import asyncio
import sys
import os
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from models.entities import Campaign, PipelineJob, JobStatusEnum
from services.job_service.job_service import (
    initialize_new_job,
    process_pending_job_with_llm,
    send_prompt_to_video_api,
    poll_video_processing_status,
    update_job_status
)
from config import settings


def demo_pipeline():
    print("="*70)
    print("DEMONSTRATION OF VIDEO UGC PIPELINE")
    print("="*70)
    
    # Check environment
    print("\n1. Checking environment configuration...")
    
    checks = [
        ("GROK_API_KEY or HF_API_KEY", settings.GROK_API_KEY or settings.HF_API_KEY),
        ("HF_SPACE_MODEL", settings.HF_SPACE_MODEL),  # Updated for new approach
        ("GOOGLE_CREDENTIALS_PATH", settings.GOOGLE_CREDENTIALS_PATH),
        ("DATABASE_URL", settings.DATABASE_URL)
    ]
    
    for name, value in checks:
        if value:
            print(f"   ✓ {name} is set")
        else:
            print(f"   ⚠ {name} is NOT set")
    
    print(f"\n   Current database: {settings.DATABASE_URL}")
    print(f"   Current video model: {settings.HF_SPACE_MODEL}")  # Updated info
    
    # Create session
    db = SessionLocal()
    
    try:
        print("\n2. Creating a demo campaign...")
        
        # Create a demo campaign
        demo_campaign = Campaign(
            name="Demo Coffee Campaign",
            briefing_text="Create a warm and inviting video showcasing our artisanal coffee brewing process. "
                         "Show close-ups of coffee beans being ground, steam rising from a freshly brewed cup, "
                         "and satisfied customers enjoying their drinks in a cozy atmosphere. "
                         "Duration: 30-40 seconds. Target: coffee enthusiasts aged 25-45. "
                         "Style: high-quality, warm lighting, slow-motion shots of coffee preparation."
        )
        
        db.add(demo_campaign)
        db.commit()
        db.refresh(demo_campaign)
        
        print(f"   ✓ Campaign '{demo_campaign.name}' created with ID: {demo_campaign.id}")
        print(f"   ✓ Briefing text: {demo_campaign.briefing_text[:100]}...")
        
        print("\n3. Initializing a job for this campaign...")
        
        # Initialize a job for this campaign
        job = initialize_new_job(db, demo_campaign.id)
        print(f"   ✓ Job initialized with ID: {job.id}")
        print(f"   ✓ Initial status: {job.status.value}")
        
        print("\n4. Processing job with LLM to generate a prompt...")
        
        # Process the job with LLM to generate a prompt
        llm_success = asyncio.run(process_pending_job_with_llm(db))
        
        # Refresh the job to get the latest status
        db.refresh(job)
        print(f"   ✓ LLM processing result: {'Success' if llm_success else 'Failed'}")
        print(f"   ✓ New status: {job.status.value}")
        
        if job.status == JobStatusEnum.PROMPT_GENERATED:
            print(f"   ✓ Generated prompt: {job.prompt[:150]}...")
        else:
            print(f"   ⚠ Job did not reach PROMPT_GENERATED status. Current status: {job.status.value}")
            
            # For demo purposes, let's simulate successful processing
            if job.status == JobStatusEnum.FAILED:
                print("   - Simulating successful prompt generation for demo...")
                update_job_status(
                    db, 
                    job.id, 
                    JobStatusEnum.PROMPT_GENERATED, 
                    prompt="Create a cinematic shot of coffee beans being poured into a grinder, "
                           "followed by slow-motion footage of coffee grounds being brewed, "
                           "and ending with steam rising from a fresh cup of coffee in warm lighting."
                )
                db.refresh(job)
                print(f"   ✓ Simulated prompt generation, status: {job.status.value}")
        
        print("\n5. Sending prompt to video generation service (Hugging Face Spaces)...")
        
        # Send the prompt to the video generation service (new approach)
        if job.status == JobStatusEnum.PROMPT_GENERATED:
            # In a real scenario, this would call the actual Hugging Face Space
            # For demo, we'll simulate this step
            print("   - Simulating video generation using Hugging Face Spaces...")
            update_job_status(db, job.id, JobStatusEnum.PROCESSING_VIDEO)
            db.refresh(job)
            print(f"   ✓ Simulated sending to video generation service, status: {job.status.value}")
        else:
            print(f"   ⚠ Cannot send to video generation service, job status is {job.status.value}")
        
        print("\n6. Simulating video processing completion...")
        
        # Simulate the video being processed
        mock_video_url = "https://drive.google.com/file/d/demo_video_id/view?usp=sharing"
        update_job_status(db, job.id, JobStatusEnum.COMPLETED, video_url=mock_video_url)
        db.refresh(job)
        
        print(f"   ✓ Video processing simulated, status: {job.status.value}")
        print(f"   ✓ Video URL: {job.video_url}")
        
        print("\n7. Final state verification...")
        
        # Verify the final state
        final_campaign = db.query(Campaign).filter(Campaign.id == demo_campaign.id).first()
        final_job = db.query(PipelineJob).filter(PipelineJob.id == job.id).first()
        
        print(f"   ✓ Campaign '{final_campaign.name}' still exists")
        print(f"   ✓ Job status: {final_job.status.value}")
        print(f"   ✓ Job has video URL: {'Yes' if final_job.video_url else 'No'}")
        
        print("\n" + "="*70)
        print("PIPELINE DEMONSTRATION COMPLETE")
        print("This shows how the system processes a campaign from start to finish:")
        print("PENDING → PROMPT_GENERATED → PROCESSING_VIDEO → COMPLETED")
        print("With new approach: Using Hugging Face Spaces for cost-free video generation")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up: remove the demo records
        try:
            db.delete(job)
            db.delete(demo_campaign)
            db.commit()
            print("\n✓ Demo cleanup completed")
        except Exception as e:
            print(f"\n⚠ Could not clean up demo records: {str(e)}")
        
        db.close()


def show_system_info():
    print("\nSYSTEM INFORMATION")
    print("-"*30)
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Video Generation: {settings.HF_SPACE_MODEL}")  # Updated for new approach
    print(f"LLM Provider: {'Grok' if settings.GROK_API_KEY else 'Hugging Face' if settings.HF_API_KEY else 'None configured'}")
    print(f"Google Drive: {'Configured' if settings.GOOGLE_CREDENTIALS_PATH else 'Not configured'}")
    
    # Show all available job statuses
    print(f"\nAvailable Job Statuses:")
    for status in JobStatusEnum:
        print(f"  - {status.value}")


if __name__ == "__main__":
    print("Video UGC Pipeline Demo - NEW APPROACH")
    print("=====================================")
    print("Using free Hugging Face Spaces for video generation")
    print("")
    
    show_system_info()
    demo_pipeline()