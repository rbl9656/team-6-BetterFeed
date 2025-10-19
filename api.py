from fastapi import FastAPI
import os
from dotenv import load_dotenv
from supabase import create_client

# load environment variables
load_dotenv()
app = FastAPI()

# set up supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)
# authenticate user with service key
supabase.postgrest.auth(os.getenv("SUPABASE_SERVICE_KEY"))

'''
main entities
'''

# endpoint to get all posts
@app.get("/posts")
def get_all_posts():
    apiresponse = supabase.table('posts').select('*').execute()
    return apiresponse.data

# endpoint to get one username by post id
@app.get("/username/{post_id}")
def get_username_by_post_id(post_id: str):
    apiresponse = supabase.table('posts').select('*,profiles(username)').eq('id', post_id).execute()
    if apiresponse.data:
        return apiresponse.data[0]['profiles']['username']
    else:
        return {"error": "Post not found"}
    
# endpoint to create a new post with validation
@app.post("/posts")
def create_post(post: dict):
    required = ['user_id', 'title', 'content', 'article_url']
    for field in required:
        if field not in post:
            return {'error': f'Missing required "{field}" field'}
    apiresponse = supabase.table('posts').insert(post).execute()
    return apiresponse.data

# endpoint toupdate post title by id
@app.put("/posts/{post_id}")
def update_post_title(post_id: str, updated_title: str):
    apiresponse = supabase.table('posts').update({'title': updated_title}).eq('id', post_id).execute()
    return apiresponse.data

# endpoint todelete post by id
@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    apiresponse = supabase.table('posts').delete().eq('id', post_id).execute()
    return apiresponse.data