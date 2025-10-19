from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from supabase import create_client

# load environment variables
load_dotenv()
app = FastAPI()

# set up supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY")
)
# authenticate user with service key
supabase.postgrest.auth(os.getenv("SUPABASE_SERVICE_KEY"))


def check_post_exists(post_id: str):
    post = supabase.table("posts").select("*").eq("id", post_id).execute()
    if not post.data:
        return (False, "Post not found")
    return (True, post.data[0])


def check_user_exists(user_id: str):
    user = supabase.table("profiles").select("*").eq("id", user_id).execute()
    if not user.data:
        return (False, "User not found")
    return (True, user.data[0])


def check_interaction_exists(user_id: str, post_id: str, interaction_type: str):
    interaction = (
        supabase.table("interactions")
        .select("*")
        .eq("user_id", user_id)
        .eq("post_id", post_id)
        .eq("interaction_type", interaction_type)
        .execute()
    )
    if not interaction.data:
        return (False, "Interaction not found")
    return (True, interaction.data[0])


def validate_interaction(interaction: dict):
    required = ["user_id", "post_id", "interaction_type"]
    for field in required:
        if field not in interaction:
            return (False, f'Missing required "{field}" field')
    # check if interaction type is valid
    if interaction["interaction_type"] not in ["like", "save"]:
        return (False, "Invalid interaction type")
    # check if post exists
    post = check_post_exists(interaction["post_id"])
    if not post[0]:
        return (False, post[1])
    # check if user exists
    user = check_user_exists(interaction["user_id"])
    if not user[0]:
        return (False, user[1])
    # check if interaction already exists
    interaction = check_interaction_exists(
        interaction["user_id"],
        interaction["post_id"],
        interaction["interaction_type"],
    )
    if interaction[0]:
        return (False, "Interaction already exists")
    return (True, "Interaction is valid")


"""
main entities
"""


# endpoint to get all posts
@app.get("/posts")
def get_all_posts():
    apiresponse = supabase.table("posts").select("*").execute()
    return apiresponse.data


# endpoint to get one username by post id
@app.get("/username/{post_id}")
def get_username_by_post_id(post_id: str):
    apiresponse = (
        supabase.table("posts")
        .select("*,profiles(username)")
        .eq("id", post_id)
        .execute()
    )
    if apiresponse.data:
        return apiresponse.data[0]["profiles"]["username"]
    else:
        raise HTTPException(status_code=404, detail="Post not found")


# endpoint to create a new post with validation
@app.post("/posts")
def create_post(post: dict):
    required = ["user_id", "title", "content", "article_url"]
    for field in required:
        if field not in post:
            raise HTTPException(
                status_code=400, detail=f'Missing required "{field}" field'
            )
    # check if user exists
    user = check_user_exists(post["user_id"])
    if not user[0]:
        raise HTTPException(status_code=404, detail=user[1])
    apiresponse = supabase.table("posts").insert(post).execute()
    return apiresponse.data


# endpoint toupdate post title by id
@app.put("/posts/{post_id}")
def update_post_title(post_id: str, updated_title: str):
    # check if post exists
    post = check_post_exists(post_id)
    if not post[0]:
        raise HTTPException(status_code=404, detail=post[1])
    apiresponse = (
        supabase.table("posts")
        .update({"title": updated_title})
        .eq("id", post_id)
        .execute()
    )
    return apiresponse.data


# endpoint todelete post by id
@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    # check if post exists
    post = check_post_exists(post_id)
    if not post[0]:
        raise HTTPException(status_code=404, detail=post[1])
    apiresponse = supabase.table("posts").delete().eq("id", post_id).execute()
    return apiresponse.data


# endpoint to create a new interaction
@app.post("/interactions")
def create_interaction(interaction: dict):
    validation = validate_interaction(interaction)
    if not validation[0]:
        raise HTTPException(status_code=400, detail=validation[1])
    apiresponse = supabase.table("interactions").insert(interaction).execute()
    return apiresponse.data


@app.get("/interactions/{post_id}")
def get_interactions_by_post_id(post_id: str):
    post = check_post_exists(post_id)
    if not post[0]:
        raise HTTPException(status_code=404, detail=post[1])
    apiresponse = (
        supabase.table("interactions")
        .select("*")
        .eq("post_id", post_id)
        .execute()
    )
    return apiresponse.data
