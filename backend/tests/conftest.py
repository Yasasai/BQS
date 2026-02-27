
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys

# Add project root (parent of backend) to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from unittest.mock import patch, MagicMock

# Mock init_db and sync_opportunities before importing app
with patch("backend.app.core.database.init_db"), \
     patch("backend.app.services.sync_manager.sync_opportunities"), \
     patch("backend.sync_manager.sync_opportunities_async", return_value=None):
    from backend.app.main import app
    from backend.app.core.database import Base, get_db


# Use file-based SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed baseline data
    db = TestingSessionLocal()
    from backend.app.models import Role, OppScoreSection
    db.add_all([
        Role(role_id=1, role_code="GH", role_name="Global Head"),
        Role(role_id=2, role_code="PH", role_name="Practice Head"),
        Role(role_id=3, role_code="SH", role_name="Sales Head"),
        Role(role_id=4, role_code="SA", role_name="Solution Architect"),
        Role(role_id=5, role_code="SP", role_name="Sales Person")
    ])
    
    required_sections = [
        ("STRAT", "Strategic Fit", 1, 0.15),
        ("WIN", "Win Probability", 2, 0.15),
        ("FIN", "Financial Value", 3, 0.15),
        ("COMP", "Competitive Position", 4, 0.10),
        ("FEAS", "Delivery Feasibility", 5, 0.10),
        ("CUST", "Customer Relationship", 6, 0.10),
        ("RISK", "Risk Exposure", 7, 0.10),
        ("PROD", "Product / Service Compliance", 8, 0.05),
        ("LEGAL", "Legal & Commercial Readiness", 9, 0.10)
    ]
    for code, name, order, weight in required_sections:
        db.add(OppScoreSection(section_code=code, section_name=name, display_order=order, weight=weight))
    
    db.commit()
    db.close()
    
    yield
    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
