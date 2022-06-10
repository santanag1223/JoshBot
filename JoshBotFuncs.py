from unicodedata import name
from discord import *
from random  import randint
from typing  import List
import requests
import json
import os

NC = "<:NickCoin:984228076131074058>"

greeting_msgs    = ["hi", "hello", "whats up", "what's up", "hey", "yo", "ayo", "aye", "whats good", "what's good"]
greeting_replies = ["Hug me Brotha!", "What's poppin'", "What, Damn?!", "What's up my n-", "Hey baby :kissing_heart:", "Que pasa guey"]

# for leaderboard formatting
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

#-#-#- Profile Helpers -#-#-#
def create_profile(usr: Member):
    """
    Creates a user's JSON file with default values.\n
    Should only be called from the Profiles Directory.
    """

    stats = {}
    stats["rank"]      = "Recruit"
    stats["coins"]     = 0
    stats["clutches"]  = 0
    stats["game"]      = {}
    stats["craps_record"] = {"w": 0, "l": 0}
    stats["bj_record"] = {"w": 0, "l": 0}
    stats["net"]       = 0
    
    usrFile = open((str(usr) + ".JSON"), "w")
    json.dump(stats, usrFile, indent=4)
    usrFile.close()

    return stats

def get_profile(usr: Member):
    """
    Returns a dictionary of the user's data from their JSON file.
    """

    os.chdir("Profiles")
    
    if (str(usr) + ".JSON") in os.listdir():
        usrFile = open((str(usr) + ".JSON"), "r")
        profile = json.load(usrFile)
        
    else:
        profile = create_profile(usr)

    os.chdir("..")

    return profile

def set_profile(usr: Member, newProfile: dict):
    """
    Replaces a user's JSON file with another dictonary.\n
    Should first get_profile() and then modifiy and use update_profile().
    """
    
    os.chdir("Profiles")
    
    if (str(usr) + ".JSON") in os.listdir():
        # overwrite old profile
        usrFile = open((str(usr) + ".JSON"), "w")
        json.dump(newProfile, usrFile, indent=4)

    os.chdir("..")

def set_field(usr: Member, field: str, newData):
    """
    Sets one of the fields in the user's JSON file to newData.
    """

    os.chdir("Profiles")
    
    if (str(usr) + ".JSON") in os.listdir():
        # load old profile info
        usrFile = open((str(usr) + ".JSON"), "r")
        profile = json.load(usrFile)
        usrFile.close()
        
        # change coin value
        profile[field] = newData

        # overwrite old profile
        usrFile = open((str(usr) + ".JSON"), "w")
        json.dump(profile, usrFile, indent=4)

    os.chdir("..")

def get_nickname(usr: Member):
    if usr.nick != None: return usr.nick
    name = str(usr).split("#")[0]

    return name

def get_profile_embed(msg: Message):

    profile = get_profile(msg.author)
    
    embed = Embed(title = "User Stats", 
                  color = Color.blue())

    bj_wins = profile["bj_record"]["w"]
    bj_loss = profile["bj_record"]["l"]
    if bj_loss == 0: bj_loss = 1
    c_wins =  profile["craps_record"]["w"]
    c_loss =  profile["craps_record"]["l"]
    if c_loss == 0: c_loss = 1

    embed.set_author(name = msg.author.display_name, icon_url = msg.author.avatar_url)
    embed.add_field(name="C$G Ranking: ", value = profile["rank"], inline = False)
    embed.add_field(name=f"NickCoin {NC} Balance: ", value = profile["coins"], inline = False)
    embed.add_field(name="Net Winnings: ", value = profile["net"], inline = False)
    embed.add_field(name="Black Jack W/L: ", value = f"{bj_wins} | {bj_loss} | {bj_wins/bj_loss}", inline = False)
    embed.add_field(name="Craps W/L: ", value = f"{c_wins} | {c_loss} | {c_wins/c_loss}", inline = False)
    embed.add_field(name="Number of Clutches: ", value = profile["clutches"], inline = False)

    return embed
    
def get_leaderboard(msg: Message, stat: int):
    os.chdir("Profiles")

    leaderboard = {}

    for prof in os.listdir():
        currProf = open(prof, "r")
        numStat  = int(currProf.readlines()[stat].split("|")[1])
        
        leaderboard[prof.replace(".JSON","")] = numStat
        currProf.close()

    os.chdir("..")

    sortedProfs = sorted(leaderboard, key= lambda ele:leaderboard[ele], reverse=True)
    
    if (stat == 1): boardtitle = f"NickCoin {NC} Leaderboard"
    else:           boardtitle = "Clutch Leaderboard"

    embed = Embed(title = boardtitle, 
                  color = Color.blue())

    place = 1
    for prof in sortedProfs:
        embed.add_field(name = ordinal(place) + " - " +  str(prof), value = str(leaderboard[prof]), inline = False)
        place += 1

    return embed

def get_reply(greeting_list) -> str:
    rand = randint(0, len(greeting_list) - 1)
    
    return greeting_list[rand]

def check_keywords(word: str, keywords: List[str]) -> bool:
    for keyword in keywords:
        if keyword == word: return True
    return False

def get_ye_quote():
    response = requests.get("https://api.kanye.rest/")
    json_data = json.loads(response.text)
    quote = json_data["quote"] + " - Kanye West"
    return quote

class Craps():
    dicesum = 0
    user   = None   
    player = ""
    rolls = []

    def __init__(self, msg: Message, bet: int) -> None:
        dice1 = randint(1,6)
        dice2 = randint(1,6)
        self.dicesum = dice1 + dice2
        self.user  = msg.author
        self.name  = get_nickname(msg.author)
        self.bet   = bet
        self.rolls = []
        self.rolls.append(dice1)
        self.rolls.append(dice2)
    
    def win_game(self):

        winnings = int(self.bet * 1.5)

        profile = get_profile(self.user)
        profile["coins"] += winnings
        profile["craps_record"]["w"] += 1
        profile["net"]   += winnings
        set_profile(self.user, profile)

        embed = Embed(title = f":money_mouth: {self.name}, You Won! +{winnings} NickCoin {NC} :money_mouth:", 
                              color = Color.blue())
        embed.add_field(name="Your Rolls:", value=":game_die: :game_die: :wave:", inline=False)
        
        count = 1
        total = 0
        for roll in self.rolls:
            embed.add_field(name = ordinal(count) + " Die :game_die:", value=roll, inline=True)
            total += roll
            if count % 2 == 0:
                embed.add_field(name="Roll Total:", value=total, inline=False)
                total = 0
            count +=1
        return embed
        
    def lose_game(self):

        losses = self.bet

        profile = get_profile(self.user)
        profile["coins"] -= losses
        profile["craps_record"]["l"] += 1
        profile["net"]   -= losses
        set_profile(self.user, profile)
        
        embed = Embed(title = f":regional_indicator_l: {self.name}, You Loss! -{losses} NickCoin {NC} :regional_indicator_l:", 
                              color = Color.red())
        embed.add_field(name="Your Rolls:", value= ":game_die: :game_die: :wave:", inline=False)
        
        count = 1
        total = 0
        for roll in self.rolls:
            embed.add_field(name = ordinal(count) + " Die :game_die:", value=roll, inline=True)
            total += roll
            if count % 2 == 0:
                embed.add_field(name="Roll Total:", value=total, inline=False)
                total = 0
            count +=1
        return embed

    def get_result(self) -> str:
        if self.dicesum == 7 or self.dicesum == 11: 
            return self.win_game()
        elif self.dicesum == 2 or self.dicesum == 3 or self.dicesum == 12: 
            return self.lose_game()
        else:
                dice3 = randint(1,6)
                dice4 = randint(1,6)
                self.rolls.append(dice3)
                self.rolls.append(dice4)
                
                if (dice3 + dice4) < 7:
                    return self.win_game()
                else:
                    return self.lose_game()
