import discord
from discord.ext import commands
import requests
from typing import Optional

# Initialize bot
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# MyMemory Translation API (Free, No API Key Required)
TRANSLATION_API = "https://api.mymemory.translated.net/get"

SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "zh": "Chinese", "id": "Indonesian",
    "ar": "Arabic", "hi": "Hindi", "ko": "Korean", "th": "Thai", "tr": "Turkish",
    "vi": "Vietnamese", "pl": "Polish", "nl": "Dutch", "ro": "Romanian", "cs": "Czech",
    "hu": "Hungarian", "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish",
    "el": "Greek", "he": "Hebrew", "uk": "Ukrainian", "ca": "Catalan", "sk": "Slovak"
}

@bot.event
async def on_ready():
    print(f'✅ Translate Bot logged in as {bot.user}')

def translate_text(text: str, target_lang: str, source_lang: str = "en") -> Optional[str]:
    """Translate text using MyMemory API (Free - No API Key needed)."""
    try:
        if not text or not target_lang:
            return None
            
        langpair = f"{source_lang}|{target_lang}"
        params = {"q": text, "langpair": langpair}
        
        response = requests.get(TRANSLATION_API, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("responseStatus") == 200:
            translated_text = result.get("responseData", {}).get("translatedText")
            if translated_text and translated_text.strip():
                return translated_text
        return None
    except Exception as e:
        print(f"Translation error: {e}")
        return None

@bot.command(name='translate')
async def translate(ctx, target_lang: str, *, text: str):
    """Translate text. Usage: $translate es Hello"""
    target_lang = target_lang.lower()
    
    if target_lang not in SUPPORTED_LANGUAGES:
        await ctx.send(f"❌ Language '{target_lang}' not supported.")
        return
    
    async with ctx.typing():
        translated = translate_text(text, target_lang, "en")
    
    if translated:
        embed = discord.Embed(title="Translation", color=discord.Color.blue())
        embed.add_field(name="Original", value=text[:1024], inline=False)
        embed.add_field(name=f"Translated ({SUPPORTED_LANGUAGES[target_lang]})", value=translated[:1024], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Translation failed.")


