"""
Script to test the API functionality directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from fastapi.testclient import TestClient

def test_api_endpoints():
    client = TestClient(app)
    
    # Test the root endpoint
    response = client.get("/")
    print(f"Root endpoint status: {response.status_code}")
    print(f"Root endpoint response: {response.json()}")
    
    # Test creating a campaign
    test_campaign_data = {
        "name": "Test Campaign API",
        "briefing_text": "This is a test campaign to verify API functionality. It must be at least fifty characters long to pass validation."
    }
    
    response = client.post("/api/campaigns/", json=test_campaign_data)
    print(f"\nCampaign creation status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Campaign creation response: {response.json()}")
        campaign_id = response.json().get('id')
        
        # Try to list campaigns
        response = client.get("/api/campaigns/")
        print(f"\nCampaign listing status: {response.status_code}")
        if response.status_code == 200:
            print(f"Campaign listing response: {response.json()}")
    else:
        print(f"Campaign creation error: {response.text}")

if __name__ == "__main__":
    test_api_endpoints()