# Whisper Transcription Setup

This document explains how to set up OpenAI Whisper transcription for voice responses in EchoForms.

## Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key to use the Whisper API
2. **Database Migration**: Run the migration script to add the `transcribed_text` column

## Setup Steps

### 1. Install Dependencies

```bash
cd echo-forms-backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Add your OpenAI API key to your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run Database Migration

```bash
python migrate_transcription.py
```

This will add the `transcribed_text` column to the `form_response_fields` table.

### 4. Restart the Backend Server

```bash
python main.py
```

## How It Works

1. **Voice Recording**: When a user records a voice response, the audio file is uploaded to B2 storage
2. **Automatic Transcription**: The backend automatically calls OpenAI Whisper API to transcribe the audio
3. **Database Storage**: The transcribed text is stored in the `transcribed_text` column
4. **API Response**: The transcription is included in API responses for form response fields

## API Changes

The `FormResponseField` model now includes:
- `transcribed_text`: The transcribed text from the voice file
- `response_time`: Duration of the recording in seconds

## Error Handling

- If transcription fails, the form submission continues without the transcribed text
- Errors are logged but don't block the form submission process
- The `transcribed_text` field will be `null` if transcription fails

## Cost Considerations

- OpenAI Whisper API charges per minute of audio processed
- Consider implementing rate limiting for production use
- Monitor API usage through OpenAI dashboard

## Testing

To test the integration:

1. Create a form with voice questions
2. Record a voice response
3. Submit the form
4. Check the database for the `transcribed_text` field
5. Verify the transcription accuracy

## Troubleshooting

### Common Issues

1. **"No module named 'openai'"**: Run `pip install -r requirements.txt`
2. **"Invalid API key"**: Check your `.env` file and ensure the API key is correct
3. **"Column does not exist"**: Run the migration script
4. **Transcription fails silently**: Check server logs for error messages

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

This will show detailed logs of the transcription process.
