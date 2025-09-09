-- Add new columns for translation, categories, and sentiment to form_response_fields table
ALTER TABLE form_response_fields 
ADD COLUMN IF NOT EXISTS translated_text TEXT,
ADD COLUMN IF NOT EXISTS categories JSON,
ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20) DEFAULT 'neutral';

-- Add language column to form_responses table
ALTER TABLE form_responses 
ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';

-- Add comments for documentation
COMMENT ON COLUMN form_response_fields.translated_text IS 'English translation of the response text if original was in another language';
COMMENT ON COLUMN form_response_fields.categories IS 'JSON array of categories extracted from the response text';
COMMENT ON COLUMN form_response_fields.sentiment IS 'Sentiment analysis result: positive, negative, or neutral';
COMMENT ON COLUMN form_responses.language IS 'Language code of the response (e.g., en, es, fr, de)';

-- Create index on language column for better query performance
CREATE INDEX IF NOT EXISTS idx_form_responses_language ON form_responses(language);

-- Update existing records to have default language as 'en'
UPDATE form_responses 
SET language = 'en' 
WHERE language IS NULL;
