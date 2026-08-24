import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import discord
import random
from discord.ext import commands
from bot_logic import gen_pass, coinflip
import requests
import math
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import asyncio
import tensorflow as tf
import numpy as np
import re   
from PIL import Image

current_player = None
board = [[' ' for _ in range(3)] for _ in range(3)]  
intents = discord.Intents.all()
intents.message_content = True
intents.messages = True 
intents.guilds = True 

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event 
async def on_ready():
    print(f'We have logged in as {bot.user}')

MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"  # Loading model... this may take a while on first run
tokenizer = None
model = None
device = None

def build_ai_prompt(user_input: str) -> str:
    return (
        "You are a friendly, helpful, and natural conversational assistant. "
        "Read the user's message and respond in a fluent, human-like way. "
        "If the user writes in Indonesian, answer in Indonesian. "
        "If the user writes in English, answer in English. "
        "Keep the response natural, brief, and polite. "
        "Do not mention that you are an AI, and do not add extra system text.\n\n"
        f"User: {user_input}\nAssistant:"
    )

async def generate_ai_reply(user_input: str) -> str:
    global tokenizer, model, device
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"AI compute device: {device}")
        if device.type == "cpu":
            print("Warning: No CUDA GPU detected. The model will run on CPU unless CUDA is installed and available.")
        model.to(device)

    prompt = build_ai_prompt(user_input)
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = inputs.to(device)
    pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id

    def generate_blocking():
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=256,
                pad_token_id=pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                do_sample=True,
                top_k=40,
                top_p=0.92,
                temperature=0.8,
                repetition_penalty=1.1,
                num_return_sequences=1,
            )
            generated = outputs[0]
            reply_tokens = generated[inputs.input_ids.shape[-1]:]
            reply = tokenizer.decode(reply_tokens, skip_special_tokens=True).strip()
            return reply

    reply = await asyncio.to_thread(generate_blocking)
    if not reply:
        return "Maaf, saya tidak bisa menjawab dengan benar sekarang. Coba lagi nanti."
    return reply
try:
    tm_model = tf.keras.models.load_model("keras_model2.h5", compile=False)
    with open("labels2.txt", "r") as f:
        tm_labels = [line.strip() for line in f.readlines()]
except Exception as e:
    print("Failed to load image model:", e)
    tm_model = None
    tm_labels = []

TRANSLATION_API = "https://api.mymemory.translated.net/get"
SUPPORTED_LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic", "hy": "Armenian",
    "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian",
    "bg": "Bulgarian", "ca": "Catalan", "ceb": "Cebuano", "zh": "Chinese", "co": "Corsican",
    "hr": "Croatian", "cs": "Czech", "da": "Danish", "nl": "Dutch", "en": "English",
    "eo": "Esperanto", "et": "Estonian", "tl": "Filipino", "fi": "Finnish", "fr": "French",
    "fy": "Frisian", "gl": "Galician", "ka": "Georgian", "de": "German", "el": "Greek",
    "gu": "Gujarati", "ht": "Haitian Creole", "ha": "Hausa", "haw": "Hawaiian", "he": "Hebrew",
    "hi": "Hindi", "hu": "Hungarian", "is": "Icelandic", "ig": "Igbo", "id": "Indonesian",
    "ga": "Irish", "it": "Italian", "ja": "Japanese", "jv": "Javanese", "kn": "Kannada",
    "kk": "Kazakh", "km": "Khmer", "ko": "Korean", "ku": "Kurdish", "ky": "Kyrgyz",
    "lo": "Lao", "la": "Latin", "lv": "Latvian", "lt": "Lithuanian", "lb": "Luxembourgish",
    "mk": "Macedonian", "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam", "mt": "Maltese",
    "mi": "Maori", "mr": "Marathi", "mn": "Mongolian", "my": "Myanmar", "ne": "Nepali",
    "no": "Norwegian", "or": "Odia", "ps": "Pashto", "fa": "Persian", "pl": "Polish",
    "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian", "ru": "Russian", "sm": "Samoan",
    "gd": "Scottish Gaelic", "sr": "Serbian", "st": "Sesotho", "sn": "Shona", "sd": "Sindhi",
    "si": "Sinhala", "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "es": "Spanish",
    "su": "Sundanese", "sw": "Swahili", "sv": "Swedish", "tg": "Tajik", "ta": "Tamil",
    "tt": "Tatar", "te": "Telugu", "th": "Thai", "tr": "Turkish", "tk": "Turkmen",
    "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur", "uz": "Uzbek", "vi": "Vietnamese",
    "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu"
}

def translate_text(text, target_lang, source_lang="en"):
    """Translate text using MyMemory free API (no key required)."""
    try:
        if not text or not target_lang:
            return None
            
        langpair = f"{source_lang}|{target_lang}"
        params = {
            "q": text,
            "langpair": langpair
        }
        
        response = requests.get(TRANSLATION_API, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # Check if response is successful
        if result.get("responseStatus") == 200:
            translated_text = result.get("responseData", {}).get("translatedText")
            if translated_text and translated_text.strip():
                return translated_text
        
        return None
    except requests.exceptions.Timeout:
        print(f"Translation timeout for: {text}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Connection error translating: {text}")
        return None
    except Exception as e:
        print(f"Translation error: {type(e).__name__}: {e}")
        return None

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if msg.content.startswith('$'):
        await bot.process_commands(msg)
        return
    try:
        if not msg.content or len(msg.content) > 1000:
            return
        reply = await generate_ai_reply(msg.content)
        if reply and len(reply) > 2000:
            fname = f"reply_{msg.id}.txt"
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(reply)
                await msg.channel.send("Reply too long — sending as a .txt file:", file=discord.File(fname))
            finally:
                try:
                    os.remove(fname)
                except Exception:
                    pass
        else:
            await msg.channel.send(reply)
    except Exception as e:
        print("Error generating reply:", e)
        fallback = random.choice([
            "Hmm, I'm not sure I SERIOUSLY understood that, can you SERIOUSLY rephrase?",
            "I couldn't say a SERIOUSLY reply just now. Try again SERIOUSLY?",
        ])
        await msg.channel.send(fallback)

Weather_api_key = "Weather api key here"
def get_weather(city):
    url = "http://api.weatherapi.com/v1/current.json"
    
    params = {
        "key": Weather_api_key,
        "q": city,
        "lang": "id"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        print(data)
        return None

    return {
        "city": data["location"]["name"],
        "country": data["location"]["country"],
        "temp": data["current"]["temp_c"],
        "feels_like": data["current"]["feelslike_c"],
        "condition": data["current"]["condition"]["text"],
        "humidity": data["current"]["humidity"],
        "wind": data["current"]["wind_kph"]
    }

bot.command()
async def hello(ctx):
    await ctx.send(f"Hi! I'm {bot.user} \U0001f642")
    await ctx.send(60*'=')
    await ctx.send(f'1. Saya bisa membantumu untuk menghasilkan kata sandi dengan ketik $pw')
    await ctx.send(f'2. Saya bisa membantumu mencari arti kata slang dengan ketik $dt <kata kapital> contoh $dt CRINGE')
    await ctx.send(f'3. Saya bisa membantumu membuat emoji dengan ketik $dt <kata> contoh $dt marah') 
    await ctx.send(f'4. Saya bisa membantumu memberikan gambar acak anjing dengan ketik $dog') 
    await ctx.send(f'5. Saya bisa membantumu memberikan gambar acak bebek dengan ketik $duck') 
    await ctx.send(f'6. Saya bisa membantumu memberikan meme acak local hari ini dengan ketik $meme')
    await ctx.send(f'7. Saya bisa membantumu memberikan coinflip dengan ketik $coinflip')
    await ctx.send(f'8. Saya bisa membantumu memberikan random dice dengan ketik $dice')
    await ctx.send(f'9. Saya bisa membantumu memperbarui versi bot ketik $unload lalu enter ketik $load lalu enter dan ketik $load lalu enter')
    await ctx.send(f'10. Saya bisa membantumu debug(memperbaiki) error dari bot ketik $reload')
    await ctx.send(f'11. Saya bisa membantumu +(tambah), -(kurang), x(kali), /(bagi), exponent(pangkat), %(modulo) contoh $tambah 1 2')
    await ctx.send(f'12. Saya bisa membantumu membuat spam contoh $repeat 2 ayo bangun')
    await ctx.send(f'13. Saya bisa membantumu menulis(overwrite), baca(read only latest note), tambahkan(append) $tulis 11 ayo bangun; $baca; $tambahkan hello world')
    await ctx.send(f'14. Saya bisa membantumu mencari keyword dari sebuah kalimat IDN dengan ketik $analisis <kalimat> contoh $analisis saya suka dia dan dia adalah anugerah')
    await ctx.send(f'15. Saya bisa membantumu mencari keyword dari sebuah kalimat ENG dengan ketik $analysis <kalimat> contoh $analysis I love you')
    await ctx.send(f'16. Saya bisa membantumu mendapatkan sentiment dari sebuah kalimat any language dengan ketik $sentiment <kalimat> atau $sentiment_vander <kalimat> contoh $sentiment I love you')
    await ctx.send(f'17. Waktu sekarang $waktu')
    await ctx.send(f'18. Simpan Lokal, upload file lalu tuliskan $simpan')
    await ctx.send(f'19. klasifikasi pipit/merpati/jenis daun upload file lalu ketik $klasifikasi atau $daun')
    await ctx.send(f'20. deteksi object upload file lalu $deteksi')
    await ctx.send(f'21. Menghasilkan nama dan gambar acak pokemon $go')
    await ctx.send(f'22. Berdiskusi dengan LLM Google Gemini $gemini')    
    await ctx.send(f'23. Melihat semua file dalam local drive $local_drive')
    await ctx.send(f'24. Menujukan file tentu dari local files folder $showfile <namefile>')
    await ctx.send(f'25. Bermain tictactoe dengan ketik $tictactoe <@opponent player> example $tictactoe @elvan1309 dan $place row collumn example $place 1 2')    
    await ctx.send(f'26. Bermain music dengan ketik /play <judul lagu (lenkgap)> example /play justin bieber you smile')
    await ctx.send(f'27. Bantuan/saran ketik $help') 
    await ctx.send(60*'=')
    await ctx.send(f'daftar kata: CRINGE, BRB, LOL, GG, AFK, CREEPY(dev.)')
    await ctx.send(f'daftar kata penghasil emoji: marah, terbahak, keren, sedih, senyum, ok(dev.)')
    await ctx.send(f'Silakan pilih permintaanmu')

@bot.command()
async def ping(ctx):
    """Responds with 'Pong!' and the latency."""
    latency = bot.latency * 1000
    await ctx.send(f'Pong! Latency: {latency:.2f} ms')

@bot.command()
async def calc(ctx, op: str, left: float, right: float):
    ops = {'add': left + right, 'min': left - right, 'times': left * right, 'divide': left / right if right != 0 else 'Division by zero', 'exp': left ** right, 'mod': left % right}
    result = ops.get(op.lower(), 'Invalid operation')
    await ctx.send(result)

@bot.command()
async def meme(ctx):
    files = os.listdir("images")
    images = [f for f in files if f.endswith(".jpg")]

    chosen = random.choice(images)
    print("Chosen:", chosen)

    await ctx.send(file=discord.File(f"images/{chosen}"))

def get_dog_image_url():
    url = 'https://random.dog/woof.json'
    res = requests.get(url)
    data = res.json()
    return data['url']

@bot.command('dog')
async def dog(ctx):
    image_url = get_dog_image_url()
    await ctx.send(image_url)

def get_duck_image_url():
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']

@bot.command('duck')
async def duck(ctx):
    image_url = get_duck_image_url()
    await ctx.send(image_url)

@bot.command()
async def tulis(ctx, *, my_string: str):
    with open('kalimat.txt', 'w', encoding='utf-8') as t:
        t.write(my_string)

@bot.command()
async def tambahkan(ctx, *, my_string: str):
    with open('kalimat.txt', 'a', encoding='utf-8') as t:
        t.write("\n" + my_string)

@bot.command()
async def baca(ctx):
    with open('kalimat.txt', 'r', encoding='utf-8') as t:
        document = t.read()
    await ctx.send(document)

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)

@bot.command()
async def passgen(ctx, length: int = 10):
    """Generate a random password (shortcut: $pass)"""
    password = gen_pass(length)
    await ctx.send(f"🔑 Your generated password: `{password}`")

@bot.command(name="pass")
async def pass_command(ctx, length: int = 10):
    """Alias dari passgen"""
    password = gen_pass(length)
    await ctx.send(f"🔐 Generated password: `{password}`")

@bot.command()
async def bye(ctx):
    """Responds with a smile emoji"""
    await ctx.send("😀")

@bot.command()
async def coinflip(ctx):
    """Flips a coin."""
    num = random.randint(1, 2)
    if num == 1:
        await ctx.send("It's Head!")
    else:
        await ctx.send("It's Tail!")

@bot.command()
async def dice(ctx):
    nums = random.randint(1, 6)
    await ctx.send(f'It is {nums}!')

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}') 

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Sends the avatar of a member."""
    member = member or ctx.author
    await ctx.send(member.avatar.url)

@bot.command()
async def serverinfo(ctx):
    """Sends information about the server."""
    guild = ctx.guild
    info = (
        f"Server Name: {guild.name}\n"
        f"Server ID: {guild.id}\n"
        f"Owner: {guild.owner}\n"
        f"Member Count: {guild.member_count}\n"
        f"Created At: {discord.utils.format_dt(guild.created_at)}\n"
    )
    await ctx.send(info)

 

@bot.command()
async def local_drive(ctx):
    try:
        folder_path = "./files"
        files = os.listdir(folder_path)
        file_list = "\n".join(files)
        await ctx.send(f"Files in the files folder:\n{file_list}")
    except FileNotFoundError:
        await ctx.send("Folder not found.")

@bot.command()
async def showfile(ctx, filename):
    """Sends a file as an attachment."""
    folder_path = "./files/"
    file_path = os.path.join(folder_path, filename)
    try:
        await ctx.send(file=discord.File(file_path))
    except FileNotFoundError:
        await ctx.send(f"File '{filename}' not found.")

@bot.command()
async def deletefile(ctx, filename):
    """Deletes a file from the local drive."""
    folder_path = "./files/"
    file_path = os.path.join(folder_path, filename)
    try:
        os.remove(file_path)
        await ctx.send(f"File '{filename}' has been deleted.")
    except FileNotFoundError:
        await ctx.send(f"File '{filename}' not found.")

@bot.command()
async def simpan(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = attachment.filename
            await attachment.save(f"./files/{file_name}")
            await ctx.send(f"Menyimpan {file_name}")
    else:
        await ctx.send("Anda lupa mengunggah :(")

@bot.command()
async def listfiles(ctx):
    folder_path = "./files/"
    try:
        files = os.listdir(folder_path)
        if files:
            file_list = "\n".join(files)
            await ctx.send(f"Files in the files folder:\n{file_list}")
        else:
            await ctx.send("No files found in the folder.")
    except FileNotFoundError:
        await ctx.send("Folder not found.")


@bot.command()
async def floor(ctx, number: float):
    """Returns the floor of a number."""
    await ctx.send(math.floor(number))

@bot.command()
async def ceil(ctx, number: float):
    """Returns the ceiling of a number."""
    await ctx.send(math.ceil(number))

@bot.command()
async def pilah(ctx, *, barang: str):
    """Bot Pemilah Sampah — memberi tahu tempat sampah yang tepat berdasarkan nama barang."""
    barang = barang.lower()
    sampah = {
        'plastik': 'kuning (plastik)', 'botol': 'kuning (plastik)',
        'kertas': 'biru (kertas)', 'koran': 'biru (kertas)', 'karton': 'biru (kertas)',
        'kaca': 'hijau (kaca)',
        'kaleng': 'abu-abu (logam)', 'besi': 'abu-abu (logam)', 'logam': 'abu-abu (logam)',
        'sisa makanan': 'coklat (organik)', 'daun': 'coklat (organik)', 'buah': 'coklat (organik)'
    }
    for key, value in sampah.items():
        if key in barang:
            await ctx.send(f"Masukkan ke tempat sampah **{value}**")
            return
    await ctx.send("Maaf, saya belum tahu jenis sampah itu. Coba masukkan nama lain!")

@bot.command()
async def bmi(ctx, weight: float, height: float):
    """Menghitung Body Mass Index (BMI) berdasarkan berat (kg) dan tinggi (m)."""
    if height <= 0:
        await ctx.send("Tinggi harus lebih besar dari nol.")
        return
    bmi_value = weight / (height ** 2)
    await ctx.send(f"Your BMI is: {bmi_value:.2f}")

@bot.command()
async def prime(ctx, number: int):
    """Memeriksa apakah sebuah angka adalah bilangan prima."""
    if number <= 1:
        await ctx.send(f"{number} is not a prime number.")
        return
    for i in range(2, int(math.sqrt(number)) + 1):
        if number % i == 0:
            await ctx.send(f"{number} is not a prime number.")
            return
    await ctx.send(f"{number} is a prime number.")

@bot.command()
async def factorial(ctx, number: int):
    """Menghitung faktorial dari sebuah angka."""
    if number < 0:
        await ctx.send("Faktorial tidak didefinisikan untuk angka negatif.")
        return
    result = math.factorial(number)
    await ctx.send(f"{number}! = {result}")

@bot.command()
async def gcd(ctx, a: int, b: int):
    """Menghitung Greatest Common Divisor (GCD) dari dua angka."""
    result = math.gcd(a, b)
    await ctx.send(f"GCD of {a} and {b} is: {result}")

@bot.command()
async def lcm(ctx, a: int, b: int):
    """Menghitung Least Common Multiple (LCM) dari dua angka."""
    if a == 0 or b == 0:
        await ctx.send("LCM tidak didefinisikan untuk angka nol.")
        return
    result = abs(a * b) // math.gcd(a, b)
    await ctx.send(f"LCM of {a} and {b} is: {result}")

@bot.command()
async def iseven(ctx, number: int):
    if number % 2 == 0:
        await ctx.send(f"{number} is an even number.")

@bot.command()
async def isodd(ctx, number: int):
    if number % 2 == 1:
        await ctx.send(f"{number} is an odd number.")

@bot.command()
async def money(ctx, amount: float, from_currency: str, to_currency: str):
    prompt = (
        f"You are an assistant that converts currencies. Convert {amount} {from_currency.upper()} "
        f"to {to_currency.upper()}. Give a numeric converted amount rounded to two decimals, "
        "and a one-line note saying this is an AI-generated approximation."
    )
    try:
        reply = await generate_ai_reply(prompt)
        await ctx.send(reply)
    except Exception as e:
        await ctx.send("Error generating conversion via AI.")


@bot.command()
async def weather(ctx, *, city: str):
    try:
        weather = get_weather(city)
        if not weather:
            await ctx.send("Kota tidak ditemukan.")
            return

        message = (
            f"Cuaca di {weather['city']}, {weather['country']}\n"
            f"Suhu: {weather['temp']}°C\n"
            f"Terasa seperti: {weather['feels_like']}°C\n"
            f"Kondisi: {weather['condition']}\n"
            f"Kelembapan: {weather['humidity']}%\n"
            f"Angin: {weather['wind']} km/h"
        )
        await ctx.send(message)
    except requests.exceptions.ConnectionError:
        await ctx.send("Error: Tidak bisa koneksi ke server cuaca. Cek internet Anda.")
    except requests.exceptions.Timeout:
        await ctx.send("Error: Timeout saat ambil cuaca. Coba lagi nanti.")
    except KeyError as e:
        await ctx.send(f"Error: Data cuaca tidak lengkap. Key missing: {e}")
    except Exception as e:
        await ctx.send(f"Error: {type(e).__name__}: {e}")
        print("weather exception:", repr(e))

@bot.command()
async def joke(ctx):
    prompt = "Tell me a short, clean joke. Just the joke, no extra commentary."
    try:
        reply = await generate_ai_reply(prompt)
        await ctx.send(reply)
    except Exception:
        await ctx.send("Error generating joke via AI.")

@bot.command()
async def ai(ctx, *, prompt: str):
    """Ask the AI assistant a question or start a natural conversation."""
    if not prompt.strip():
        await ctx.send("Tolong beri saya pertanyaan atau pesan yang ingin dijawab.")
        return
    async with ctx.typing():
        try:
            reply = await generate_ai_reply(prompt)
            await ctx.send(reply)
        except Exception as e:
            print("AI command error:", e)
            await ctx.send("Error generating AI response. Silakan coba lagi.")

@bot.command(name='translate')
async def translate_cmd(ctx, target_lang: str, *, text: str):
    """Translate text to target language. Usage: $translate es Hello"""
    target_lang = target_lang.lower()
    
    if target_lang not in SUPPORTED_LANGUAGES:
        available = ", ".join(list(SUPPORTED_LANGUAGES.keys())[:10])
        await ctx.send(f"❌ Language '{target_lang}' not supported.\n**Available:** {available}...\nUse `$languages` for full list.")
        return
    
    async with ctx.typing():
        translated = translate_text(text, target_lang, "en")
    
    if translated:
        embed = discord.Embed(
            title="Translation",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=text[:1024], inline=False)
        embed.add_field(name=f"Translated ({SUPPORTED_LANGUAGES[target_lang]})", value=translated[:1024], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Translation failed for '{text[:50]}...'. Please check:\n• Your internet connection\n• The text is valid\n• Language code '{target_lang}' is correct")

bot.run("Your discord Token here ")
