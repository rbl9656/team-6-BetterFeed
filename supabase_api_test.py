import requests
import os
from dotenv import load_dotenv
import supabase
from supabase import Client, create_client

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase.postgrest.auth(SUPABASE_SERVICE_KEY)  # authenticates the user

def access_data(table, query, filter = None):
    return supabase.table(table).select(query).execute()

def insert_data(table, insert):
    return supabase.table(table).insert(insert).execute()

# retrieves all data from posts table
all_posts = access_data('posts','*')

# retrieves all usernames from profiles table
all_usernames = access_data('profiles','username')

# retreives user_id through the related table profiles
all_user_ids = access_data('posts','*,profiles(id,username)')

post = {
    'user_id' : 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55',
    'title' : 'Test Post from Python',
    'content' : 'This is content inserted to test RLS',
    'article_url' : 'https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DdQw4w9WgXcQ&ved=2ahUKEwiEzf3guayQAxVwhIkEHTMePWYQtwJ6BAgKEAI&usg=AOvVaw0aHtehaphMhOCAkCydRLZU'
}

insert_data('posts', post)
print(access_data('posts','title')) # verify that the data was inserted correctly by checking for title