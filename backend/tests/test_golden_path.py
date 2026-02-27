
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from backend.app.models import Opportunity, AppUser, Role, OppScoreSection, OppScoreVersion

@pytest.fixture
def seed_data(db_session):
    # Create a test user
    user = AppUser(user_id="user1", email="test@example.com", display_name="Test User")
    db_session.add(user)
    
    # Create a test opportunity starting at ASSIGNED_TO_SA
    opp = Opportunity(
        opp_id="opp1",
        opp_number="OPT-001",
        opp_name="Test Opportunity",
        customer_name="Test Customer",
        deal_value=100000.0,
        crm_last_updated_at=datetime.now(timezone.utc),
        is_active=True,
        workflow_status="ASSIGNED_TO_SA",
        assigned_sa_id="user1"
    )
    db_session.add(opp)
    db_session.commit()
    return user, opp

def test_list_opportunities(client, seed_data):
    response = client.get("/api/opportunities/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
    assert any(item["id"] == "opp1" for item in data["items"])

def test_opportunity_detail(client, seed_data):
    response = client.get("/api/opportunities/opp1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Opportunity"

def test_assign_role(client, seed_data):
    response = client.post("/api/opportunities/opp1/assign", json={
        "role": "SA",
        "user_id": "user1",
        "assigned_by": "admin"
    })
    assert response.status_code == 200
    
    # Verify assignment in DB
    response = client.get("/api/opportunities/opp1")
    assert response.json()["assigned_sa"] == "Test User"

def test_start_assessment(client, seed_data):
    response = client.post("/api/opportunities/opp1/start-assessment", json={
        "sa_name": "Test User"
    })
    assert response.status_code == 200
    
    # Verify status
    response = client.get("/api/opportunities/opp1")
    assert response.json()["workflow_status"] == "UNDER_ASSESSMENT"

def test_save_draft(client, seed_data):
    response = client.post("/api/scoring/opp1/draft", json={
        "user_id": "user1",
        "sections": [
            {"section_code": "STRAT", "score": 4, "notes": "Good fit"}
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_submit_scoring(client, seed_data):
    # First save a draft to ensure version exists
    client.post("/api/scoring/opp1/draft", json={
        "user_id": "user1",
        "sections": [
            {"section_code": "STRAT", "score": 4, "notes": "Good fit"}
        ]
    })
    
    response = client.post("/api/scoring/opp1/submit", json={
        "user_id": "user1",
        "sections": [
            {"section_code": "STRAT", "score": 4, "notes": "Good fit"}
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_combined_review(client, seed_data):
    response = client.get("/api/scoring/opp1/combined-review")
    assert response.status_code == 200
    # Basic check - should return info about the opportunity
    assert response.json()["opp_id"] == "opp1"

def test_approve_workflow(client, seed_data):
    # Mock statuses so it can be approved
    user, opp = seed_data
    opp.gh_approval_status = "PENDING"
    opp.ph_approval_status = "PENDING"
    opp.sh_approval_status = "PENDING"
    
    response = client.post("/api/opportunities/opp1/approve", json={
        "role": "GH",
        "decision": "APPROVED",
        "user_id": "user1"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("backend.app.routers.batch_sync.batch_sync_opportunities")
def test_batch_sync_start(mock_sync, client):
    response = client.post("/api/batch-sync/start", json={
        "batch_size": 5,
        "sync_name": "test_sync"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "started"
    assert mock_sync.called

@patch("backend.app.routers.batch_sync.get_sync_status")
@patch("backend.app.routers.batch_sync.get_synced_count")
def test_batch_sync_status(mock_count, mock_status, client):
    mock_status.return_value = {
        "sync_name": "test_sync",
        "current_offset": 10,
        "total_synced": 10,
        "last_sync_at": datetime.now(timezone.utc),
        "is_complete": False
    }
    mock_count.return_value = 10
    
    response = client.get("/api/batch-sync/status?sync_name=test_sync")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["total_synced"] == 10
