
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Role

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

roles = db.query(Role).all()
for r in roles:
    print(f"ID: {r.role_id}, Code: {r.role_code}, Name: {r.role_name}")
db.close()
