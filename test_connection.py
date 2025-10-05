import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load your Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Debug: Check if variables are loaded
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("ERROR: Environment variables not loaded!")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_ANON_KEY: {SUPABASE_ANON_KEY}")
    print("\nMake sure your .env file exists and contains:")
    print("SUPABASE_URL=your_url_here")
    print("SUPABASE_ANON_KEY=your_key_here")
    exit(1)

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("Testing Supabase Connection for Article Reels App")
print("=" * 60)
print()

# ============================================
# Test 1: Read all profiles
# ============================================
print("TEST 1: Reading all profiles")
print("-" * 40)
try:
    response = supabase.table('profiles').select("*").execute()
    print(f"Successfully connected to Supabase!")
    print(f"Found {len(response.data)} user profiles")
    
    # Show first profile as example
    if response.data:
        first_user = response.data[0]
        print(f"   Example user: {first_user['username']} ({first_user['email']})")
    print()
except Exception as e:
    print(f"Error reading profiles: {e}")
    print()

# ============================================
# Test 2: Read reels with real article data
# ============================================
print("TEST 2: Reading reels with real article data")
print("-" * 40)
try:
    response = supabase.table('reels') \
        .select("*, profiles(username)") \
        .order('created_at', desc=True) \
        .limit(5) \
        .execute()
    
    print(f"Successfully queried reels with JOIN!")
    print(f"Found {len(response.data)} reels (showing top 5)")
    print()
    
    for reel in response.data:
        print(f"   Title: {reel['title']}")
        print(f"   Creator: @{reel['profiles']['username']}")
        print(f"   Views: {reel['view_count']}")
        print(f"   Article URL: {reel['article_url'][:60]}...")
        print()
except Exception as e:
    print(f"Error reading reels: {e}")
    print()

# ============================================
# Test 3: Get interaction statistics
# ============================================
print("TEST 3: Analyzing interactions")
print("-" * 40)
try:
    # Count total likes
    likes = supabase.table('interactions') \
        .select("*", count='exact') \
        .eq('interaction_type', 'like') \
        .execute()
    
    # Count total saves
    saves = supabase.table('interactions') \
        .select("*", count='exact') \
        .eq('interaction_type', 'save') \
        .execute()
    
    print(f"Successfully analyzed interactions!")
    print(f"Total likes: {likes.count}")
    print(f"Total saves: {saves.count}")
    print()
except Exception as e:
    print(f"Error reading interactions: {e}")
    print()

# ============================================
# Test 4: Find most popular reel
# ============================================
print("TEST 4: Finding most popular reel")
print("-" * 40)
try:
    # Get reel with most views
    response = supabase.table('reels') \
        .select("title, view_count, article_url, profiles(username)") \
        .order('view_count', desc=True) \
        .limit(1) \
        .execute()
    
    if response.data:
        top_reel = response.data[0]
        print(f"Most popular reel:")
        print(f"   Title: '{top_reel['title']}'")
        print(f"   Creator: @{top_reel['profiles']['username']}")
        print(f"   Views: {top_reel['view_count']:,}")
        print(f"   URL: {top_reel['article_url']}")
    print()
except Exception as e:
    print(f"Error finding popular reel: {e}")
    print()

# ============================================
# Test 5: Test RLS (should fail without auth)
# ============================================
print("TEST 5: Testing Row Level Security")
print("-" * 40)
try:
    # Try to insert a reel without authentication
    test_reel = {
        "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "article_url": "https://test.com/article",
        "title": "Test Reel"
    }
    
    response = supabase.table('reels').insert(test_reel).execute()
    print(f"WARNING: Insert succeeded without auth (RLS might not be configured)")
    print()
except Exception as e:
    print(f"RLS is working! Unauthorized insert was blocked:")
    print(f"   Error: {str(e)[:80]}...")
    print(f"   Note: This is expected behavior - only authenticated users should insert")
    print()

# ============================================
# Test 6: Verify article URLs are real
# ============================================
print("TEST 6: Verifying article URLs from API")
print("-" * 40)
try:
    response = supabase.table('reels') \
        .select("article_url") \
        .limit(3) \
        .execute()
    
    print("Sample article URLs from NewsAPI:")
    for i, reel in enumerate(response.data, 1):
        print(f"   {i}. {reel['article_url']}")
    print()
except Exception as e:
    print(f"Error reading article URLs: {e}")
    print()

# ============================================
# Test 7: Complex query - Most active user
# ============================================
print("TEST 7: Finding most active user")
print("-" * 40)
try:
    response = supabase.table('profiles') \
        .select("username, reels(count)") \
        .execute()
    
    # Find user with most reels
    if response.data:
        user_reel_counts = [(user['username'], len(user['reels'])) for user in response.data]
        user_reel_counts.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Most active creators:")
        for username, count in user_reel_counts[:3]:
            print(f"   @{username}: {count} reels")
    print()
except Exception as e:
    print(f"Error finding active users: {e}")
    print()

# ============================================
# Test 8: Get reels with their interaction counts
# ============================================
print("TEST 8: Reels with engagement metrics")
print("-" * 40)
try:
    response = supabase.table('reels') \
        .select("title, view_count, interactions(count)") \
        .order('view_count', desc=True) \
        .limit(3) \
        .execute()
    
    print(f"Top reels by engagement:")
    for reel in response.data:
        interaction_count = len(reel['interactions'])
        print(f"   '{reel['title'][:60]}...'")
        print(f"      Views: {reel['view_count']} | Interactions: {interaction_count}")
    print()
except Exception as e:
    print(f"Error getting engagement metrics: {e}")
    print()

print("=" * 60)
print("Database testing complete!")
print()
print("All data is now from real news articles via NewsAPI!")
print()
print("Next steps:")
print("  1. Review any errors above")
print("  2. Verify RLS policies are blocking unauthorized access")
print("  3. Check that joins are working correctly")
print("  4. When ready, add AI summary functionality in future scaling!")
print("  5. Ready to build your app!")