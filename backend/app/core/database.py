import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL dan SUPABASE_KEY harus diisi di .env")

# Inisialisasi Client Supabase
supabase: Client = create_client(url, key)

print("✅ Supabase Client Initialized")