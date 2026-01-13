from sqlalchemy import inspect, text
from database import engine, Base, SessionLocal

def run_heal():
    """Universal Self-Healing for all tables in the system."""
    print("🔧 Running BQS Universal Auto-Heal...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    db = SessionLocal()
    try:
        # Iterate over all models defined in database.py (Base)
        for table_name, table in Base.metadata.tables.items():
            if table_name in existing_tables:
                # Check for missing columns
                db_columns = {col['name'] for col in inspector.get_columns(table_name)}
                model_columns = {col.name for col in table.columns}
                missing = model_columns - db_columns
                
                if missing:
                    print(f"⚠️  Missing {len(missing)} columns in '{table_name}': {missing}")
                    for col_name in missing:
                        col = table.columns[col_name]
                        # Correctly compile the type for PostgreSQL (e.g. VARCHAR, FLOAT)
                        col_type = col.type.compile(dialect=engine.dialect)
                        nullable = "NULL" if col.nullable else "NOT NULL"
                        
                        sql = f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}'
                        print(f"   🔧 Adding: {col_name}")
                        db.execute(text(sql))
                        db.commit()
            else:
                # If table doesn't exist, Create everything (Base.metadata handles this usually)
                print(f"🆕 Creating new table: {table_name}")
    
        # Ensure all tables themselves exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema is synchronized.")
        
    except Exception as e:
        print(f"❌ Auto-Heal Failure: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_heal()
