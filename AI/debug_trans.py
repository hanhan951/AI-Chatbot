import requests
import json

# Debug translation function
TRANSLATION_API = "https://api.mymemory.translated.net/get"

def debug_translate(text, target_lang, source_lang="en"):
    """Debug version of translate function"""
    try:
        langpair = f"{source_lang}|{target_lang}"
        params = {
            "q": text,
            "langpair": langpair
        }
        
        print(f"URL: {TRANSLATION_API}")
        print(f"Params: {params}")
        
        response = requests.get(TRANSLATION_API, params=params, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
        response.raise_for_status()
        result = response.json()
        
        print(f"Full Response: {json.dumps(result, indent=2)}")
        
        if result.get("responseStatus") == 200:
            translated = result.get("responseData", {}).get("translatedText", None)
            print(f"✅ Translated: {translated}")
            return translated
        else:
            print(f"❌ Response status not 200: {result.get('responseStatus')}")
            return None
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test cases
test_cases = [
    ("Hello world", "es", "en"),
    ("Hola", "en", "es"),
    ("Selamat pagi", "en", "id"),
]

print("=== MyMemory Translation Debug ===\n")

for text, target, source in test_cases:
    print(f"\nTest: '{text}' (from {source} to {target})")
    result = debug_translate(text, target, source)
    print("-" * 50)
