import os
import requests
import json
from typing import Optional, Tuple

def detect_language_and_translate(text: str) -> Tuple[Optional[str], bool, str]:
    """
    Detect if text is non-English and translate it to English using Gemini.
    
    Args:
        text: The text to analyze and potentially translate
        
    Returns:
        Tuple of (translated_text, is_translated, language_code)
        - translated_text: English translation if non-English, None if already English
        - is_translated: Boolean indicating if translation was performed
        - language_code: Detected language code (e.g., 'en', 'es', 'fr', 'de')
    """
    if not text or not text.strip():
        return None, False, "en"
    
    try:
        # Use Gemini to detect language and translate if needed
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY not found")
            return None, False, "en"
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
        Analyze the following text and determine if it's in English or another language.
        
        Text: "{text}"
        
        If the text is in English, respond with: {{"is_english": true, "translated_text": null, "language_code": "en"}}
        
        If the text is in another language, translate it to English and respond with: {{"is_english": false, "translated_text": "translated_english_text", "language_code": "detected_language_code"}}
        
        For language_code, use standard ISO 639-1 codes like: en, es, fr, de, it, pt, ru, ja, ko, zh, ar, etc.
        
        IMPORTANT: Respond with ONLY valid JSON. Do not use markdown code blocks, do not add any extra text, do not explain anything. Just return the JSON object.
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1000
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Parse the JSON response
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_content = content.strip()
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]  # Remove ```json
                if cleaned_content.startswith("```"):
                    cleaned_content = cleaned_content[3:]   # Remove ```
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]  # Remove trailing ```
                
                cleaned_content = cleaned_content.strip()
                print(f"Cleaned Gemini response: {cleaned_content}")
                
                parsed = json.loads(cleaned_content)
                is_english = parsed.get("is_english", True)
                translated_text = parsed.get("translated_text")
                language_code = parsed.get("language_code", "en")
                
                # Ensure proper UTF-8 encoding for translated text
                if translated_text and isinstance(translated_text, str):
                    translated_text = translated_text.encode('utf-8').decode('utf-8')
                
                if is_english:
                    return None, False, language_code
                else:
                    return translated_text, True, language_code
            except json.JSONDecodeError as e:
                print(f"Failed to parse Gemini response: {content}")
                print(f"JSON decode error: {str(e)}")
                return None, False, "en"
        else:
            print("No candidates in Gemini response")
            return None, False, "en"
            
    except Exception as e:
        print(f"Error in language detection and translation: {str(e)}")
        return None, False, "en"

def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of text using Gemini.
    
    Args:
        text: The text to analyze for sentiment
        
    Returns:
        Sentiment as string: "positive", "negative", or "neutral"
    """
    if not text or not text.strip():
        return "neutral"
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY not found")
            return "neutral"
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
        Analyze the sentiment of the following text.
        
        Text: "{text}"
        
        Determine if the sentiment is positive, negative, or neutral.
        
        Respond with ONLY one word: "positive", "negative", or "neutral"
        Do not add any other text or explanation.
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 10
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            sentiment = content.strip().lower()
            
            if sentiment in ["positive", "negative", "neutral"]:
                return sentiment
            else:
                print(f"Unexpected sentiment response: {sentiment}")
                return "neutral"
        else:
            print("No candidates in sentiment response")
            return "neutral"
            
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "neutral"

def extract_categories_from_text(text: str) -> list:
    """
    Extract categories from text using Gemini.
    
    Args:
        text: The text to analyze for categories
        
    Returns:
        List of category dictionaries
    """
    if not text or not text.strip():
        return []
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY not found")
            return []
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
        Analyze the following text and extract relevant categories/topics.
        
        Text: "{text}"
        
        Return a JSON array of categories, where each category has:
        - name: category name in ENGLISH (short, 2-3 words)
        - confidence: confidence score (0.0 to 1.0)
        - keywords: list of relevant keywords in ENGLISH
        
        IMPORTANT: 
        - Use ONLY English for category names and keywords
        - Translate any non-English terms to English
        - Keep category names concise and professional
        
        Example format:
        [
            {{"name": "Product Quality", "confidence": 0.9, "keywords": ["quality", "defect", "issue"]}},
            {{"name": "Customer Service", "confidence": 0.8, "keywords": ["service", "support", "help"]}}
        ]
        
        Respond with ONLY valid JSON array. Do not use markdown code blocks, do not add any extra text, do not explain anything. Just return the JSON array.
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Parse the JSON response
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_content = content.strip()
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]  # Remove ```json
                if cleaned_content.startswith("```"):
                    cleaned_content = cleaned_content[3:]   # Remove ```
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]  # Remove trailing ```
                
                cleaned_content = cleaned_content.strip()
                print(f"Cleaned categories response: {cleaned_content}")
                
                categories = json.loads(cleaned_content)
                if isinstance(categories, list):
                    # Ensure proper UTF-8 encoding for all text fields
                    for category in categories:
                        if 'name' in category and isinstance(category['name'], str):
                            category['name'] = category['name'].encode('utf-8').decode('utf-8')
                        if 'keywords' in category and isinstance(category['keywords'], list):
                            category['keywords'] = [
                                keyword.encode('utf-8').decode('utf-8') 
                                if isinstance(keyword, str) else keyword
                                for keyword in category['keywords']
                            ]
                    return categories
                else:
                    return []
            except json.JSONDecodeError as e:
                print(f"Failed to parse categories response: {content}")
                print(f"JSON decode error: {str(e)}")
                return []
        else:
            print("No candidates in categories response")
            return []
            
    except Exception as e:
        print(f"Error in category extraction: {str(e)}")
        return []
