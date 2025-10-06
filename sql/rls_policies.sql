-- ============================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE reels ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;

-- ============================================
-- PROFILES POLICIES
-- ============================================

-- Anyone can view all profiles (public app)
CREATE POLICY "Profiles are viewable by everyone"
    ON profiles FOR SELECT
    USING (true);

-- Users can insert their own profile (linked to auth.users)
CREATE POLICY "Users can insert their own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- ============================================
-- REELS POLICIES
-- ============================================

-- Anyone can view all reels (public feed)
CREATE POLICY "Reels are viewable by everyone"
    ON reels FOR SELECT
    USING (true);

-- Authenticated users can create reels
CREATE POLICY "Authenticated users can create reels"
    ON reels FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own reels
CREATE POLICY "Users can update their own reels"
    ON reels FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can delete their own reels
CREATE POLICY "Users can delete their own reels"
    ON reels FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- INTERACTIONS POLICIES
-- ============================================
-- Note: Interactions are publicly viewable so users can see engagement metrics 
-- (like counts, save counts) on all reels. Users can only create/delete 
-- their own interactions.

-- Anyone can view all interactions (needed for engagement metrics)
CREATE POLICY "Anyone can view all interactions"
    ON interactions FOR SELECT
    USING (true);

-- Users can create their own interactions
CREATE POLICY "Users can create their own interactions"
    ON interactions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own interactions
CREATE POLICY "Users can delete their own interactions"
    ON interactions FOR DELETE
    USING (auth.uid() = user_id);