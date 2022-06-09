from dotenv       import load_dotenv
from discord      import *
from Cards import BlackJack
from JoshBotFuncs import *
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
NC    = "<:NickCoin:984228076131074058>"

client = Client()

@client.event
async def on_message(msg: Message):
    
    # ignore messages from JoshBot
    if msg.author == client.user: return

    # If message starts with !, we need to process the message
    if msg.content.startswith("!"):
        text = str(msg.content).replace("!","").lower()

        if check_keywords(text, greeting_msgs):
            await msg.channel.send(get_reply(greeting_replies))
    
        if text == "ye" or text == "kanye":
            await msg.channel.send(get_ye_quote())

        if text == "account" or text == "profile":
            embed = get_profile_embed(msg)
            await msg.channel.send(embed=embed)

        if "leaderboard" in text:
            if "clutch" in text:
                embed = get_leaderboard(msg, 2)
                await msg.channel.send(embed=embed)
            else:
                embed = get_leaderboard(msg, 1)
                await msg.channel.send(embed=embed)
        
        if "craps" in text:
            text = text.replace("craps","").strip()

            if text == "rules" or text == "r":

                embed = Embed(title = "Craps Rules :game_die: :game_die: :wave:", 
                              color = Color.red())

                embed.add_field(name="Winning Rolls:", value = "7, 11", inline = True)
                embed.add_field(name="Losing Rolls:", value = "2, 3, 12", inline = True)
                embed.add_field(name="Other Rolls:", value = "Roll again, next total must be less than 7 to win!", inline = True)
                embed.add_field(name="Returns:", value = "1.75 x Bet", inline = True)

                await msg.channel.send(embed=embed); return

            if text == "":
                await msg.channel.send(f"You need to bet some amount of NickCoin {NC}"); return
            
            bet  = int(text)
            c = Craps(msg, bet)
            await msg.channel.send(embed = c.get_result())
        
        if "blackjack" in text:
            # process text
            text = text.replace("blackjack","").strip()
            
            # return if there isn't a bet made
            if text == "":
                await msg.channel.send(f"You need to bet some amount of NickCoin {NC}"); return
            
            # return if bet is greater than NickCoin balance
            bet     = int(text)
            profile = get_profile(msg.author)
            
            if bet > profile["coins"]:
                await msg.channel.send("boi you don't have that much money to bet."); return

            if len(profile["game"]) > 0:
                await msg.channel.send("You have an active game! Hit or Stand?"); return

            bj   = BlackJack(msg, bet, init=True)
            await msg.channel.send(embed=bj.get_next(msg))

        if "hit" in text:
            bj   = BlackJack(msg, hit=True)
            await msg.channel.send(embed=bj.get_next(msg))

        if "stand" in text:
            bj   = BlackJack(msg, hit=False)
            await msg.channel.send(embed=bj.get_next(msg))

@client.event
async def on_connect():
    print("JoshBot is online!") 

client.run(TOKEN)