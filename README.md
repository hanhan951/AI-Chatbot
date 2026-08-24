# 🤖 Chatbot (Multifunctional)

A multifunctional Discord chatbot built with **Python** as my graduation project for an online programming course.

The bot combines an **AI chatbot, utility tools, entertainment commands, file management, weather information, translation, image processing, and multiplayer games** into one Discord application.

---

## ✨ Features

### 🤖 AI Chat (LLM)

The chatbot uses the **Qwen2-1.5B-Instruct** language model to generate natural conversational responses.

**Features:**

* Natural and conversational responses
* Supports **English and Indonesian**
* Can respond to normal Discord messages
* Dedicated AI command for questions and conversations

**Command:**

```text
$ai <your message>
```

Example:

```text
$ai What is artificial intelligence?
```

---

### 🌍 Translation

The bot can translate text using a translation API.

**Command:**

```text
$translate <language_code> <text>
```

Example:

```text
$translate id Hello world
```

The bot supports many different language codes.

---

### 🌦️ Weather Information

The bot retrieves current weather information using a weather API.

**Command:**

```text
$weather <city>
```

Example:

```text
$weather Jakarta
```

**Information provided:**

* Temperature
* Weather condition
* Humidity
* Wind speed
* Feels-like temperature

---

### 🎲 Fun Commands

A collection of simple commands for entertainment:

```text
$coinflip    → Flip a coin
$dice        → Roll a dice
$meme        → Send a random meme
$dog         → Send a random dog image
$duck        → Send a random duck image
```

---

### 🧮 Math & Utility

The bot includes several mathematical and utility functions:

```text
$calc
$bmi
$prime
$factorial
$gcd
$lcm
$floor
$ceil
```

These commands can perform calculations, mathematical checks, and other utility operations.

---

### 📁 File Management

The bot can manage files stored locally.

```text
$simpan              → Save uploaded files
$listfiles           → List available files
$showfile <filename> → Send/display a specific file
$deletefile <filename> → Delete a file
```

The bot can also write, append, and read text files.

---

### ♻️ Waste Sorting

An educational waste-sorting feature that identifies common types of waste and suggests the appropriate category.

**Command:**

```text
$pilah <item>
```

Example:

```text
$pilah plastic bottle
```

---

### 🔐 Password Generator

Generate a random password with a specified length.

**Command:**

```text
$pass <length>
```

Example:

```text
$pass 12
```

---

### 🔁 Repeat Message

Repeats a message a specified number of times.

**Command:**

```text
$repeat <times> <message>
```

Example:

```text
$repeat 3 Hello!
```

---

### 🎮 Multiplayer Tic-Tac-Toe

The bot includes a multiplayer **Tic-Tac-Toe** game that allows two Discord users to play against each other.

Example:

```text
$tictactoe @opponent
```

Players can then place their marks using the appropriate game command.

---

# ⚙️ How It Works

The bot is divided into several main systems.

## 1. AI System

The AI system is responsible for generating natural language responses.

```text
build_ai_prompt()
        ↓
Creates the AI prompt
        ↓
generate_ai_reply()
        ↓
Tokenizes the input
        ↓
Qwen2-1.5B-Instruct
        ↓
Generates a response
        ↓
Discord message
```

### Main Functions

**`build_ai_prompt()`**

Creates a structured prompt for the language model and provides instructions for how the AI should respond.

**`generate_ai_reply()`**

Loads the AI model when needed, processes the user's input, generates a response, and returns the result.

The project also uses asynchronous processing so that the AI generation does not unnecessarily block the Discord bot.

---

## 2. Event Handler

The Discord bot uses event handlers to respond to Discord events.

### `on_ready()`

Runs when the bot successfully connects to Discord.

### `on_message()`

Handles incoming messages.

The bot checks whether the message starts with `$`.

```text
Message received
       ↓
Starts with "$"?
   ↙          ↘
 Yes           No
  ↓             ↓
Command       AI System
  ↓             ↓
Response      Response
```

This allows the bot to support both traditional commands and natural AI conversations.

---

## 3. Image Processing

The project also includes an image classification system using **TensorFlow/Keras**.

The model performs image preprocessing and prediction to classify uploaded images.

Required model files:

```text
keras_model2.h5
labels2.txt
```

The model and its labels are loaded when the bot starts.

---

## 4. API Integration

The bot communicates with external APIs to provide additional functionality.

### Weather API

Used to retrieve current weather information.

### Translation API

Used to translate text between different languages.

Internet access is required for these features.

---

# 🛠️ Technologies

The project was built using:

| Technology          | Purpose                   |
| ------------------- | ------------------------- |
| Python              | Main programming language |
| discord.py          | Discord bot framework     |
| Transformers        | AI model integration      |
| Qwen2-1.5B-Instruct | Large language model      |
| PyTorch             | AI model execution        |
| TensorFlow / Keras  | Image classification      |
| NumPy               | Numerical operations      |
| Pillow              | Image processing          |
| Requests            | API communication         |
| asyncio             | Asynchronous programming  |

---

# 📦 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure the Discord Bot

Create a Discord application and bot through the Discord Developer Portal.

Then configure your Discord bot token.

**Do not publish your actual bot token on GitHub.**

For example:

```python
bot.run("YOUR_DISCORD_TOKEN")
```

Replace `YOUR_DISCORD_TOKEN` with your actual token locally.

> **Security:** Never commit your real Discord token or API keys to a public repository.

---

# 📦 Required Files

Make sure the following files are available in the project:

```text
keras_model2.h5
labels2.txt
```

The project may also require local folders such as:

```text
images/
files/
```

depending on which features you use.

---

# ⚠️ Notes

* The AI model is relatively large and may require significant RAM.
* A GPU with CUDA can improve AI generation performance.
* Without a compatible GPU, the AI model can run on the CPU but may be slower.
* An internet connection is required for API-based features such as weather and translation.
* The image classification features require the appropriate `.h5` model and label files.
* Discord bot permissions and intents must be configured correctly.

---

# 🚀 Future Improvements

Possible future improvements include:

* 🎙️ Voice commands
* 🎵 Improved music player
* 🌐 Web dashboard
* 🗄️ Database integration
* 🧠 Improved AI conversation memory
* 🔑 Better security and environment-variable configuration
* 🎮 Additional multiplayer games
* ☁️ Cloud deployment for 24/7 availability

---

# 🎓 Project Purpose

This chatbot was created as my **graduation project for an online programming course**.

The project allowed me to apply and combine different programming concepts, including:

* Python programming
* Discord bot development
* Asynchronous programming
* AI and LLM integration
* API integration
* Machine learning
* Image processing
* File management
* Error handling

The goal was to create a single Discord bot that combines multiple useful and entertaining features in one application.

---

## 👨‍💻 Author

Nathaniel Ligustro William

Graduation Project — Python & Discord Bot Development

---

⭐ **Thank you for checking out my project!**
