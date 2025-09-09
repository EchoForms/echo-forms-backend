-- Add new columns for translation and categories to form_response_fields table
ALTER TABLE form_response_fields 
ADD COLUMN IF NOT EXISTS translated_text TEXT,
ADD COLUMN IF NOT EXISTS categories JSON;

-- Add comments for documentation
COMMENT ON COLUMN form_response_fields.translated_text IS 'English translation of the response text if original was in another language';
COMMENT ON COLUMN form_response_fields.categories IS 'JSON array of categories extracted from the response text';
