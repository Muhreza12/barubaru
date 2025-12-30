-- migration_images.sql - Tambah kolom gambar
BEGIN;

-- Tambah kolom untuk gambar di tabel news
ALTER TABLE news 
ADD COLUMN IF NOT EXISTS image_data BYTEA,
ADD COLUMN IF NOT EXISTS image_filename TEXT,
ADD COLUMN IF NOT EXISTS image_mime_type VARCHAR(100),
ADD COLUMN IF NOT EXISTS image_size INTEGER DEFAULT 0;

-- Index untuk pencarian cepat artikel dengan gambar
CREATE INDEX IF NOT EXISTS idx_news_image ON news ((image_data IS NOT NULL));

COMMENT ON COLUMN news.image_data IS 'Binary image data (max 5MB)';
COMMENT ON COLUMN news.image_filename IS 'Original filename';
COMMENT ON COLUMN news.image_mime_type IS 'MIME type: image/png, image/jpeg, etc';
COMMENT ON COLUMN news.image_size IS 'File size in bytes';

-- Verifikasi
SELECT 
    '✅ IMAGE MIGRATION COMPLETED!' as status,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN image_data IS NOT NULL THEN 1 END) as articles_with_images
FROM news;

COMMIT;