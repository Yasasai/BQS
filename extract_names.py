"""
Helper: Extract opportunity names from the dashboard
Based on your screenshot, here are the visible opportunity names
"""

# From your screenshot, I can see these opportunities:
DASHBOARD_OPPORTUNITIES = [
    "16985449 IAM with Sailsource 12m offsh",
    "1602737 SAS Media test PZ Cloud v 2 0",
    "1553327 revised1 IMR DDock V 2 3",
]

print("📋 Opportunity Names from Dashboard:")
print("=" * 60)
for idx, name in enumerate(DASHBOARD_OPPORTUNITIES, 1):
    print(f"{idx}. {name}")

print("\n" + "=" * 60)
print("Copy these names into fetch_by_names.py")
print("=" * 60)

# Export to text file for easy copy-paste
with open("opportunity_names.txt", "w") as f:
    for name in DASHBOARD_OPPORTUNITIES:
        f.write(f'"{name}",\n')

print("\n✅ Also saved to: opportunity_names.txt")
print("\nTo add more:")
print("1. Look at your Oracle dashboard")
print("2. Copy the full opportunity name (including the number prefix)")
print("3. Add it to the list in fetch_by_names.py")
