-- ============================================
-- SEED DATA FOR ARTICLE REELS APP
-- ============================================
-- Note: This project primarily uses Python (seed.py) for data seeding 
-- because it fetches real articles from NewsAPI.
-- 
-- To seed the database with real data, run:
--   python seed.py
--
-- The SQL below provides minimal sample data for testing purposes only.
-- ============================================

-- Sample profiles
INSERT INTO profiles (id, email, username, avatar_url) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'alice@example.com', 'alice_reads', 'https://i.pravatar.cc/150?img=1'),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'bob@example.com', 'bob_learns', 'https://i.pravatar.cc/150?img=2'),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'carol@example.com', 'carol_curious', 'https://i.pravatar.cc/150?img=3')
ON CONFLICT (id) DO NOTHING;

-- Sample reels (using placeholder article URLs)
INSERT INTO reels (user_id, article_url, title, view_count) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'https://example.com/article1', 'Sample Tech Article', 127),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'https://example.com/article2', 'Sample Science Article', 254),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'https://example.com/article3', 'Sample Space Article', 381);

-- Sample interactions
-- Note: These will only work if RLS is disabled or if using service role key
INSERT INTO interactions (user_id, reel_id, interaction_type) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 1, 'like'),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 1, 'save'),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 2, 'like')
ON CONFLICT (user_id, reel_id, interaction_type) DO NOTHING;