
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise SystemExit(
        "ERROR: SUPABASE_URL or SUPABASE_KEY is missing from .env"
    )

try:
    supabase = create_client(url, key)

    # Read only the minimum data needed to test access.
    response = (
        supabase.table("Repair")
        .select("id")
        .limit(1)
        .execute()
    )

    print("Connection successful.")
    print("Repair table is accessible.")
    print(f"Test returned {len(response.data)} record(s).")

except Exception as error:
    print("Supabase connection or permission test failed.")
    print(f"Error type: {type(error).__name__}")
    print(str(error)[:500])