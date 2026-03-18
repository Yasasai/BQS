import sys
import os
sys.path.append(os.getcwd())
try:
    from backend.app.core.database import SessionLocal
    from backend.app.routers.opportunities import get_all_opportunities

    class DummyUser:
        id = "123"
        role = "GH"

    db = SessionLocal()
    try:
        from backend.app.models import Opportunity
        db.rollback() # clear any tainted state
        total = db.query(Opportunity).count()
        print(f"RAW DB COUNT: {total}")
        
        res = get_all_opportunities(db=db, page=1, limit=50, tab="all", user_id="123", role="GH", current_user=DummyUser())
        print("DIAGNOSTIC BACKEND RESULT:")
        print(f"Items count: {len(res['items'])}")
        print(f"Total count: {res['total_count']}")
        if res['items']:
            item = res['items'][0]
            print(f"Sample item ID type: {type(item['id'])}")
            print(f"Sample item ID: {item['id']}")
            print(f"Keys in item: {item.keys()}")
            
        else:
            print("No items found using get_all_opportunities.")
            
    except Exception as e:
        db.rollback()
        try:
            res = get_all_opportunities(db=db, page=1, limit=50, tab="all", user_id="123", role="GH", current_user=DummyUser())
            print("DIAGNOSTIC BACKEND RESULT (AFTER ROLLBACK):")
            print(f"Items count: {len(res['items'])}")
            print(f"Total count: {res['total_count']}")
            if res['items']:
                item = res['items'][0]
                print(f"Sample item ID type: {type(item['id'])}")
                print(f"Sample item ID: {item['id']}")
            else:
                print("Still no items found after rollback.")
        except Exception as retry_e:
            print(f"Retry failed: {retry_e}")
        import traceback
        print(f"Original Error during diagnostic: {e}")
        traceback.print_exc()
    finally:
        db.close()
except Exception as e:
    print(f"Failed to load dependencies: {e}")
