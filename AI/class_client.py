import random
import discord
from bot_logic import gen_pass, coinflip, roll_dice


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f' Bot sudah login sebagai {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower().strip()

    if content.startswith("pass"):
        kata_sandi = gen_pass(10)
        await message.channel.send(f" Password: {kata_sandi}")

    elif content.startswith("coin"):
        hasil = coinflip()
        await message.channel.send(f" Coin: {hasil}")

    elif content.startswith("dice"):
        hasil = roll_dice()
        await message.channel.send(f" Dice: {hasil}")




client.run("Your discord token here")
