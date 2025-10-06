import os
import requests
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Load credentials - USE SERVICE KEY for seeding
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Changed from ANON_KEY
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Debug: Check if variables are loaded
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Supabase environment variables not loaded!")
    print("Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are in your .env file")
    exit(1)

if not NEWS_API_KEY:
    print("WARNING: NEWS_API_KEY not found. You'll need this to fetch articles.")

# Initialize Supabase client with SERVICE KEY (bypasses RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("Fetching real article data from NewsAPI...")
print("Using SERVICE KEY to bypass RLS for seeding...")
print("=" * 60)
print()

# ============================================
# Step 1: Create sample users first
# ============================================
print("STEP 1: Creating sample user profiles")
print("-" * 40)

sample_users = [
    {
        'id': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        'email': 'alice@example.com',
        'username': 'alice_reads',
        'avatar_url': 'https://i.pravatar.cc/150?img=1'
    },
    {
        'id': 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        'email': 'bob@example.com',
        'username': 'bob_learns',
        'avatar_url': 'https://i.pravatar.cc/150?img=2'
    },
    {
        'id': 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
        'email': 'carol@example.com',
        'username': 'carol_curious',
        'avatar_url': 'https://i.pravatar.cc/150?img=3'
    },
    {
        'id': 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
        'email': 'david@example.com',
        'username': 'david_discovers',
        'avatar_url': 'https://i.pravatar.cc/150?img=4'
    },
    {
        'id': 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55',
        'email': 'emma@example.com',
        'username': 'emma_explores',
        'avatar_url': 'https://i.pravatar.cc/150?img=5'
    }
]

try:
    for user in sample_users:
        try:
            supabase.table('profiles').insert(user).execute()
            print(f"Created user: @{user['username']}")
        except Exception as e:
            if 'duplicate key value' in str(e).lower():
                print(f"User @{user['username']} already exists (skipping)")
            else:
                print(f"Error creating user @{user['username']}: {str(e)[:100]}")
    print()
except Exception as e:
    print(f"Error in user creation: {e}")
    print()

# ============================================
# Step 2: Fetch real articles from NewsAPI
# ============================================
print("STEP 2: Fetching real articles from NewsAPI")
print("-" * 40)

# Topics to search for interesting articles
topics = [
    'technology',
    'science',
    'space',
    'artificial intelligence',
    'environment'
]

all_articles = []

for topic in topics:
    print(f"Fetching articles about: {topic}")
    
    url = f"https://newsapi.org/v2/everything"
    params = {
        'q': topic,
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'popularity',
        'pageSize': 3
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            articles = data['articles']
            print(f"  Found {len(articles)} articles")
            all_articles.extend(articles)
        else:
            print(f"  No articles found for {topic}")
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  Error fetching {topic}: {e}")

print(f"\nTotal articles fetched: {len(all_articles)}")
print()

# ============================================
# Step 3: Insert articles as posts
# ============================================
print("STEP 3: Creating posts from articles")
print("-" * 40)

user_ids = [user['id'] for user in sample_users]
post_count = 0

for i, article in enumerate(all_articles[:15]):
    if not article.get('url'):
        continue
    
    user_id = user_ids[i % len(user_ids)]
    
    post = {
        'user_id': user_id,
        'article_url': article['url'],
        'title': article['title'][:100] if article['title'] else 'Untitled Article',
        'content': article.get('description', '')[:500] if article.get('description') else '',
        'thumbnail_url': article.get('urlToImage'),
        'view_count': (i + 1) * 127
    }
    
    try:
        result = supabase.table('posts').insert(post).execute()
        post_count += 1
        print(f"Created post {post_count}: {post['title'][:50]}...")
    except Exception as e:
        print(f"Error creating post: {str(e)[:100]}")

print(f"\nSuccessfully created {post_count} posts!")
print()

# ============================================
# Step 4: Create sample interactions
# ============================================
print("STEP 4: Creating sample interactions")
print("-" * 40)

try:
    posts_response = supabase.table('posts').select('id').execute()
    post_ids = [post['id'] for post in posts_response.data]
    
    if not post_ids:
        print("No posts found to create interactions")
    else:
        import random
        interaction_count = 0
        
        for user_id in user_ids:
            num_interactions = random.randint(3, 7)
            selected_posts = random.sample(post_ids, min(num_interactions, len(post_ids)))
            
            for post_id in selected_posts:
                interaction_type = random.choice(['like', 'like', 'save'])
                
                interaction = {
                    'user_id': user_id,
                    'post_id': post_id,
                    'interaction_type': interaction_type
                }
                
                try:
                    supabase.table('interactions').insert(interaction).execute()
                    interaction_count += 1
                except Exception as e:
                    if 'duplicate key value' not in str(e).lower():
                        print(f"Error: {str(e)[:80]}")
        
        print(f"Created {interaction_count} interactions")
        print()
        
except Exception as e:
    print(f"Error creating interactions: {e}")
    print()

# ============================================
# Summary
# ============================================
print("=" * 60)
print("Database seeding complete!")
print()
print("Summary:")
print(f"  - Users: {len(sample_users)}")
print(f"  - Posts (from real articles): {post_count}")
print(f"  - Ready to test your database!")
print()
print("IMPORTANT: Your test_connection.py still uses ANON key (which is correct)")
print("           This script used SERVICE key to bypass RLS for seeding")