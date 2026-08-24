import requests
import json

# Test LibreTranslate API
API_URL = "https://libretranslate.de/translate"

test_cases = [
    {"text": "Hello world", "source": "auto", "target": "es"},
    {"text": "Comment allez-vous?", "source": "auto", "target": "en"},
    {"text": "Selamat pagi", "source": "auto", "target": "ja"},
]

print("Testing LibreTranslate API...\n")

for i, test in enumerate(test_cases, 1):
    try:
        payload = {
            "q": test["text"],
            "source": test["source"],
            "target": test["target"],
            "format": "text"
        }
        
        print(f"Test {i}:")
        print(f"  Original: {test['text']}")
        print(f"  Target Language: {test['target']}")
        
        response = requests.post(API_URL, data=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if "translatedText" in result:
            print(f"  ✅ Translation: {result['translatedText']}\n")
        else:
            print(f"  ❌ No translatedText in response\n")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")

print("\nNow testing alternative endpoint...")

# Try alternative free endpoint
ALT_API_URL = "https://api.mymemory.translated.net/get"

test_text = "Hello world"
try:
    params = {
        "q": test_text,
        "langpair": "en|es"
    }
    
    print(f"Testing MyMemory API:")
    print(f"  Original: {test_text}")
    
    response = requests.get(ALT_API_URL, params=params, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    print(f"  Response: {json.dumps(result, indent=2)}")
    
    if result.get("responseStatus") == 200:
        print(f"  ✅ Translation: {result['responseData']['translatedText']}\n")
    else:
        print(f"  ❌ Request failed\n")
        
except Exception as e:
    print(f"  ❌ Error: {str(e)}\n")
