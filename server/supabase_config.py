import os
from dotenv import load_dotenv

# Load environment variables from .env filet
load_dotenv()


class SupabaseConfig:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")  # Try both key names
        self.client = None

        # Debug information
        print(f"DEBUG: SUPABASE_URL = {self.url}")
        print(f"DEBUG: SUPABASE_KEY found = {'Yes' if self.key else 'No'}")
        print(f"DEBUG: Current working directory = {os.getcwd()}")
        print(f"DEBUG: .env file exists = {os.path.exists('.env')}")

    def get_client(self):
        """Returns the initialized Supabase client"""
        if not self.client:
            try:
                from supabase import create_client, Client

                if not self.url or not self.key:
                    missing_vars = []
                    if not self.url:
                        missing_vars.append("SUPABASE_URL")
                    if not self.key:
                        missing_vars.append("SUPABASE_ANON_KEY or SUPABASE_KEY")

                    raise ValueError(
                        f"Missing environment variables: {', '.join(missing_vars)}. Please check your .env file.")

                self.client = create_client(self.url, self.key)
                print("✅ Supabase client initialized successfully")
                return self.client

            except ImportError:
                print("Supabase module is not installed. Please install it using: pip install supabas")
                raise Exception("Supabase module not installed. Please run: pip install supabase")
            except Exception as e:
                print(f"Supabase configuration error: {e}")
                raise Exception(f"Supabase configuration error: {e}")

        return self.client

    def is_configured(self):
        """Check if Supabase is properly configured"""
        return bool(self.url and self.key)


# Global instance
supabase_config = SupabaseConfig()