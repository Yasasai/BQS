from database import engine, Opportunity, SessionLocal
from sqlalchemy import inspect, text

def run_heal():
    print("🔧 Running Manual Auto-Heal...")
    
    # Check if opportunities table exists and has all required columns
    inspector = inspect(engine)
    if 'opportunities' in inspector.get_table_names():
        db_columns = {col['name'] for col in inspector.get_columns('opportunities')}
        model_columns = {col.name for col in Opportunity.__table__.columns}
        missing = model_columns - db_columns
        
        if missing:
            print(f"⚠️  Detected {len(missing)} missing columns: {missing}")
            print("🔧 Auto-healing database schema...")
            
            db = SessionLocal()
            try:
                for col_name in missing:
                    col = Opportunity.__table__.columns[col_name]
                    col_type = col.type.compile(dialect=engine.dialect)
                    nullable = "NULL" if col.nullable else "NOT NULL"
                    
                    sql = f"ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}"
                    print(f"  Adding: {col_name}")
                    db.execute(text(sql))
                    db.commit()
                print("✓ Schema healed successfully")
            except Exception as e:
                db.rollback()
                print(f"⚠️  Warning: Could not auto-heal: {e}")
            finally:
                db.close()
        else:
            print("✓ Schema is up to date")
    else:
        print("❌ 'opportunities' table does not exist!")

if __name__ == "__main__":
    run_heal()
