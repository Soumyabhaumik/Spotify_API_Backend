from django.core.management.base import BaseCommand, CommandError
from supabase import create_client, Client
import os
from authapp.models import Song
import psycopg2  # Import your Song model


class Command(BaseCommand):
    help = "Creates the 'song' table in Supabase"

    def handle(self, *args, **options):
        """
        This method is executed when the command is run.
        """
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        SUPABASE_DB_URL = os.environ.get(
            "SUPABASE_DB_URL"
        )  # get the Supabase database url

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise CommandError(
                "Supabase URL and Key must be set as environment variables."
            )

        try:
            # Use psycopg2 to connect directly to the PostgreSQL database
            conn = psycopg2.connect(SUPABASE_DB_URL)
            cur = conn.cursor()

            # Define the CREATE TABLE SQL statement based on the Django model
            sql = """
                CREATE TABLE IF NOT EXISTS song (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    artist VARCHAR(255) NOT NULL,
                    audio_url VARCHAR(2000)
                );
                """
            # Execute the SQL query
            cur.execute(sql)
            conn.commit()

            self.stdout.write(self.style.SUCCESS(f"Successfully created table 'song'"))
        except Exception as e:
            raise CommandError(f"Failed to create table 'song': {e}")
        finally:
            if conn:
                cur.close()
                conn.close()
