import requests
import json

def test():
    try:
        url = 'http://127.0.0.1:8000/api/opportunities/'
        
        # Test GH
        r = requests.get(url, params={'tab': 'review', 'role': 'GH'})
        print(f"GH Response: {r.status_code}")
        gh_items = r.json().get('items', [])
        print(f"GH Review Names: {[i.get('name') for i in gh_items if 'Acme' in i.get('name') or 'RetailCo' in i.get('name')]}")
        
        # Test PH
        r = requests.get(url, params={'tab': 'review', 'role': 'PH', 'user_id': 'ph-001'})
        print(f"PH Response: {r.status_code}")
        ph_items = r.json().get('items', [])
        print(f"PH Review Names: {[i.get('name') for i in ph_items if 'Acme' in i.get('name') or 'RetailCo' in i.get('name')]}")
        
        # Test SH
        r = requests.get(url, params={'tab': 'review', 'role': 'SH', 'user_id': 'sh-001'})
        print(f"SH Response: {r.status_code}")
        sh_items = r.json().get('items', [])
        print(f"SH Review Names: {[i.get('name') for i in sh_items if 'Acme' in i.get('name') or 'RetailCo' in i.get('name')]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
