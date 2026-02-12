"""
Test Oracle API - Compare All URL Formats
==========================================

Tests different URL formats to find which returns the most records.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ORACLE_BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0"
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

auth = (ORACLE_USER, ORACLE_PASSWORD)

print("="*70)
print("🔍 ORACLE API COMPARISON TEST")
print("="*70)
print("Testing 4 different URL formats to find which returns most records")
print("="*70)

with httpx.Client(auth=auth, timeout=60.0) as client:
    
    results = {}

    # TEST 0: USER SPECIFIC URL
    print("\n📊 TEST 0: USER SPECIFIC URL")
    print("-"*70)
    
    url0 = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?q=StatusCode='OPEN'&totalResults=true&limit=500"
    print(f"URL: {url0}")
    
    try:
        r = client.get(url0)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("totalResults", 0)
            results["USER_URL"] = total
            print(f"✅ totalResults: {total}")
        else:
            print(f"❌ Error: {r.status_code}")
            results["USER_URL"] = 0
    except Exception as e:
        print(f"❌ Error: {e}")
        results["USER_URL"] = 0
    
    # TEST 1: RecordSet=ALLOPTIES (no quotes)
    print("\n📊 TEST 1: RecordSet=ALLOPTIES (no quotes)")
    print("-"*70)
    
    url1 = f"{ORACLE_BASE_URL}/opportunities?finder=MyOpportunitiesFinder;RecordSet=ALLOPTIES&totalResults=true&limit=1"
    print(f"URL: {url1}")
    
    try:
        r = client.get(url1)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("totalResults", 0)
            results['RecordSet=ALLOPTIES'] = total
            print(f"✅ totalResults: {total}")
        else:
            print(f"❌ Error: {r.status_code}")
            results['RecordSet=ALLOPTIES'] = 0
    except Exception as e:
        print(f"❌ Error: {e}")
        results['RecordSet=ALLOPTIES'] = 0
    
    # TEST 2: RecordSet='ALLOPTIES' (with single quotes)
    print("\n📊 TEST 2: RecordSet='ALLOPTIES' (with single quotes)")
    print("-"*70)
    
    url2 = f"{ORACLE_BASE_URL}/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&totalResults=true&limit=1"
    print(f"URL: {url2}")
    
    try:
        r = client.get(url2)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("totalResults", 0)
            results["RecordSet='ALLOPTIES'"] = total
            print(f"✅ totalResults: {total}")
        else:
            print(f"❌ Error: {r.status_code}")
            results["RecordSet='ALLOPTIES'"] = 0
    except Exception as e:
        print(f"❌ Error: {e}")
        results["RecordSet='ALLOPTIES'"] = 0
    
    # TEST 3: q=StatusCode='OPEN'
    print("\n📊 TEST 3: q=StatusCode='OPEN'")
    print("-"*70)
    
    url3 = f"{ORACLE_BASE_URL}/opportunities?q=StatusCode='OPEN'&totalResults=true&limit=1"
    print(f"URL: {url3}")
    
    try:
        r = client.get(url3)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("totalResults", 0)
            results["q=StatusCode='OPEN'"] = total
            print(f"✅ totalResults: {total}")
        else:
            print(f"❌ Error: {r.status_code}")
            results["q=StatusCode='OPEN'"] = 0
    except Exception as e:
        print(f"❌ Error: {e}")
        results["q=StatusCode='OPEN'"] = 0
    
    # TEST 4: q=OptyNumber IS NOT NULL (wildcard)
    print("\n📊 TEST 4: q=OptyNumber IS NOT NULL (wildcard)")
    print("-"*70)
    
    url4 = f"{ORACLE_BASE_URL}/opportunities?q=OptyNumber IS NOT NULL&totalResults=true&limit=1"
    print(f"URL: {url4}")
    
    try:
        r = client.get(url4)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("totalResults", 0)
            results["q=OptyNumber IS NOT NULL"] = total
            print(f"✅ totalResults: {total}")
        else:
            print(f"❌ Error: {r.status_code}")
            results["q=OptyNumber IS NOT NULL"] = 0
    except Exception as e:
        print(f"❌ Error: {e}")
        results["q=OptyNumber IS NOT NULL"] = 0
    
    # COMPARISON
    print("\n" + "="*70)
    print("📊 COMPARISON RESULTS")
    print("="*70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    for i, (url_type, count) in enumerate(sorted_results, 1):
        if i == 1:
            print(f"🥇 {url_type}: {count} records ✅ BEST!")
        elif i == 2:
            print(f"🥈 {url_type}: {count} records")
        elif i == 3:
            print(f"🥉 {url_type}: {count} records")
        else:
            print(f"   {url_type}: {count} records")
    
    print("="*70)
    
    # RECOMMENDATION
    best_url = sorted_results[0][0]
    best_count = sorted_results[0][1]
    
    print("\n💡 RECOMMENDATION:")
    print("-"*70)
    print(f"Use: {best_url}")
    print(f"Returns: {best_count} records")
    print("-"*70)
    
    # TEST FETCHING WITH BEST URL
    print("\n📊 TEST: Fetch First 3 Batches with BEST URL")
    print("-"*70)
    
    # Determine which URL to use
    if best_url == "RecordSet='ALLOPTIES'":
        base_fetch_url = f"{ORACLE_BASE_URL}/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
    elif best_url == "RecordSet=ALLOPTIES":
        base_fetch_url = f"{ORACLE_BASE_URL}/opportunities?finder=MyOpportunitiesFinder;RecordSet=ALLOPTIES"
    elif best_url == "q=StatusCode='OPEN'":
        base_fetch_url = f"{ORACLE_BASE_URL}/opportunities?q=StatusCode='OPEN'"
    else:
        base_fetch_url = f"{ORACLE_BASE_URL}/opportunities?q=OptyNumber IS NOT NULL"
    
    total_fetched = 0
    
    for batch in range(3):
        offset = batch * 50
        
        url = f"{base_fetch_url}&limit=50&offset={offset}&onlyData=true"
        
        try:
            r = client.get(url)
            
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                has_more = data.get("hasMore", False)
                
                total_fetched += len(items)
                
                print(f"\nBatch {batch + 1} (offset {offset}):")
                print(f"  Items: {len(items)}")
                print(f"  hasMore: {has_more}")
                print(f"  Total so far: {total_fetched}")
                
                if len(items) == 0:
                    print(f"  ⚠️  Empty batch")
                    break
            else:
                print(f"\nBatch {batch + 1}: Error {r.status_code}")
                break
                
        except Exception as e:
            print(f"\nBatch {batch + 1}: Error - {e}")
            break
    
    print(f"\n📊 Total fetched in test: {total_fetched}/{best_count}")

print("\n"+"="*70)
print("🏁 TEST COMPLETE")
print("="*70)
print("\n✅ Use the BEST URL in your sync script!")
print("="*70)
