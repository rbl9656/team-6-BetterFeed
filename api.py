from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
from supabase import create_client
from supabase._sync.client import SyncClient
from typing import Annotated, TypedDict

# load environment variables
load_dotenv()
app = FastAPI()

# set up supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY")
)
# authenticate user with service key
supabase.postgrest.auth(os.getenv("SUPABASE_SERVICE_KEY"))

# set up HTTPBearer for token authentication
security = HTTPBearer()


class AuthResponse(TypedDict):
    user: dict
    client: SyncClient


# auth middleware
def auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthResponse:
    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        user_client: SyncClient = create_client(
            os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY")
        )
        user_client.postgrest.auth(token)
        return {"user": response.user, "client": user_client}
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Invalid or expired token: {str(e)}"
        )


auth_deps = Annotated[AuthResponse, Depends(auth)]


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
def get_username_by_post_id(post_id: int):
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
def create_post(post: dict, auth_response: auth_deps):
    required = ["title", "content", "article_url"]
    for field in required:
        if field not in post:
            raise HTTPException(
                status_code=400, detail=f'Missing required "{field}" field'
            )
    post["user_id"] = auth_response["user"].id
    user_client = auth_response["client"]
    apiresponse = user_client.table("posts").insert(post).execute()
    return apiresponse.data


# endpoint to update post title by id
@app.put("/posts/{post_id}")
def update_post_title(
    post_id: int, updated_title: str, auth_response: auth_deps
):
    user_client = auth_response["client"]
    # check if post exists
    try:
        apiresponse = (
            user_client.table("posts")
            .update({"title": updated_title})
            .eq("id", post_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating post: {str(e)}"
        )
    if not apiresponse.data:
        raise HTTPException(
            status_code=404, detail="Post not found or unauthorized"
        )
    return apiresponse.data


# endpoint to delete post by id
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, auth_response: auth_deps):
    user_client = auth_response["client"]
    try:
        apiresponse = (
            user_client.table("posts").delete().eq("id", post_id).execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting post: {str(e)}"
        )
    if not apiresponse.data:
        raise HTTPException(
            status_code=404, detail="Post not found or unauthorized"
        )
    return apiresponse.data


# endpoint to create a new interaction
@app.post("/interactions")
def create_interaction(interaction: dict, auth_response: auth_deps):
    user_client = auth_response["client"]
    try:
        apiresponse = (
            user_client.table("interactions").insert(interaction).execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating interaction: {str(e)}"
        )
    if not apiresponse.data:
        raise HTTPException(
            status_code=400, detail="Invalid interaction or unauthorized"
        )
    return apiresponse.data


@app.get("/interactions/{post_id}")
def get_interactions_by_post_id(post_id: int):
    try:
        apiresponse = (
            supabase.table("interactions")
            .select("*")
            .eq("post_id", post_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting interactions: {str(e)}"
        )
    if not apiresponse.data:
        raise HTTPException(
            status_code=404, detail="Interactions not found or unauthorized"
        )
    return apiresponse.data


# endpoint to delete an interaction
@app.delete("/interactions/{interaction_id}")
def delete_interaction(interaction_id: int, auth_response: auth_deps):
    user_client = auth_response["client"]
    try:
        apiresponse = (
            user_client.table("interactions")
            .delete()
            .eq("id", interaction_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting interaction: {str(e)}"
        )
    if not apiresponse.data:
        raise HTTPException(
            status_code=404, detail="Interaction not found or unauthorized"
        )
    return apiresponse.data


"""
auth
"""


# endpoint to sign up new user
@app.post("/signup")
def sign_up_user(credentials: dict):
    required = ["email", "password", "username"]
    for field in required:
        if field not in credentials:
            raise HTTPException(
                status_code=400, detail=f'Missing required "{field}" field'
            )

    # create user in auth
    auth_response = supabase.auth.sign_up(
        {
            "email": credentials["email"],
            "password": credentials["password"],
        }
    )
    if auth_response.user is None:
        raise HTTPException(status_code=400, detail="Error creating user")

    # create user profile
    profile = {
        "id": auth_response.user.id,
        "email": credentials["email"],
        "username": credentials["username"],
    }
    profile_response = supabase.table("profiles").insert(profile).execute()
    return {"auth": auth_response.user, "profile": profile_response.data}


# endpoint to log in user
@app.post("/login")
def log_in_user(credentials: dict):
    required = ["email", "password"]
    for field in required:
        if field not in credentials:
            raise HTTPException(
                status_code=400, detail=f'Missing required "{field}" field'
            )

    auth_response = supabase.auth.sign_in_with_password(
        {
            "email": credentials["email"],
            "password": credentials["password"],
        }
    )
    if auth_response.user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "user": auth_response.user,
        "session": auth_response.session,
        "access_token": auth_response.session.access_token,
    }
