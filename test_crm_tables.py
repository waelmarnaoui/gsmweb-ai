
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

for table in ["Repair", "Client", "AccessorySale"]:
    try:
        result = (
            client.table(table)
            .select("*", count="exact")
            .limit(3)
            .execute()
        )

        print(f"\nTable: {table}")
        print(f"Rows returned: {len(result.data or [])}")
        print(f"Total visible rows: {result.count}")
        if result.data:
            print(f"Columns: {', '.join(result.data[0].keys())}")
    except Exception as error:
        print(f"\nTable: {table}")
        print(f"Error: {type(error).__name__}: {str(error)[:300]}")