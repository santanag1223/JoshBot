from cgitb import reset
from random       import randint
from typing       import List
from discord      import *
from JoshBotFuncs import *

BLANK_CARD = "|░░░░░░|" + "\n" + \
             "|░░░░░░|" + "\n" + \
             "|░░░░░░|" + "\n" + \
             "|░░░░░░|" + "\n" + \
             "|░░░░░░|"

class Card():
    suit    = ""
    number  = 0
    isFace  = False
    isAce   = False
    person  = ""

    def __init__(self, suit, number):
        self.suit = suit
        self.number = number

        if number < 2 or number > 10:
            self.isFace = True
            if number == 1:  self.person = "░░Ace░░"; self.isAce = True
            if number == 11: self.person = "░Jack░░"
            if number == 12: self.person = "░Queen░"
            if number == 13: self.person = "░King░░"

    def __str__(self):
        if self.isFace: 
            return f"{self.suit}░░░░░{self.suit}\n|░░░░░░|\n|{self.person}|\n|░░░░░░|\n{self.suit}░░░░░{self.suit}"
        else:
            return f"{self.suit}░░░░░{self.suit}\n|░░░░░░|\n|" + "░░{0:2d}░░░|".format(self.number) + f"\n|░░░░░░|\n{self.suit}░░░░░{self.suit}"

    def __repr__(self):
        return self.__str__()

    def formatted(self):
        return f"{self.suit}-{self.number}"

class Deck():
    cards    = list()
    shuffled = False

    def __init__(self):
        self.cards = []
        self.shuffled = False
            
    def shuffle(self):
        shuffled = list()

        for _ in range(len(self.cards)):
            if (len(self.cards) > 1):
                newCard = self.cards.pop(randint(0, len(self.cards) - 1))
            else:
                newCard = self.cards.pop()
            shuffled.append(newCard)

        self.cards = shuffled
        self.shuffled = True

    def full_deck(self):
        self.cards = []
        for suit in ["♡", "♢", "♤", "♧"]:
            for i in range(1,14):
                self.cards.append(Card(suit, i))

    def new_shuffled_deck(self):
        self.full_deck()
        self.shuffle()

    def draw_card(self):
        return self.cards.pop()

    def bj_sum(self):
        sums = [0,0]
        for card in self.cards:
            if not card.isFace:
                sums[0] += card.number
                sums[1] += card.number
            elif card.isAce:
                sums[0] += 1
                sums[1] += 11
            else:
                sums[0] += 10
                sums[1] += 10

        return sums

    def build_from_strs(self, str_cards: List[str]):
        self.cards = []
        for string in str_cards:
            newcard = Card(string.split("-")[0], int(string.split("-")[1]))
            self.cards.append(newcard)
        
        self.shuffled = True

class BlackJack():
    cards    = None
    bet      = 0
    
    usrSums  = [0,0]
    usrBest  = 0
    usrHand  = []

    dlrSums  = [0,0]
    dlrBust  = 0
    dlrHand  = []

    result  = ""

    def __init__(self, msg: Message, bet = 0, init = False, hit = False):
        self.fullDeck    = Deck()
        self.usrHand     = Deck()
        self.dlrHand     = Deck()
        self.usrSums     = [0,0]
        self.dlrSums     = [0,0]

        if init:
            self.bet = bet
            # shuffle cards
            self.fullDeck.new_shuffled_deck()
            # deal to usr
            self.usrHand.cards.append(self.fullDeck.draw_card())
            self.usrHand.cards.append(self.fullDeck.draw_card())
            # deal to dlr
            self.dlrHand.cards.append(self.fullDeck.draw_card())
            # get current hand sums
            self.usrSums = self.usrHand.bj_sum()
            self.dlrSums = self.dlrHand.bj_sum()
            # get highest number
            self.get_best_sums()

            if self.usrBest == 21: 
                self.stand_loop()
            else:
                self.result = ":hearts::diamonds: Hit or Stand?! :diamonds::hearts:"
                set_field(msg.author, "game", self.save_game())
                return
            
        else:
            # rebuild fields from player JSON
            self.load_game(msg.author)
            #print(f"[DEBUG] : Loaded user sums {self.usrSums}")
            #print(f"[DEBUG] : Loaded dealer sums {self.dlrSums}")

            # check if player hits or stands
            if hit: self.usrHand.cards.append(self.fullDeck.draw_card())
            else  : self.stand_loop()

        # handle a bust or tie
        if self.gameover: 
            self.end_game(msg.author)
            set_field(msg.author, "game", {})
        else:
            set_field(msg.author, "game", self.save_game())
            self.result = "Hit or Stand?!"

    def get_best_sums(self):
        if self.usrSums[1] < 22: self.usrBest = self.usrSums[1]
        else:                    self.usrBest = self.usrSums[0]

        if self.dlrSums[1] < 22: self.dlrBest = self.dlrSums[1]
        else:                    self.dlrBest = self.dlrSums[0]
        

    def next_state(self):
        # Determine Game Outcome
        if self.dlrBest > 21:
            self.result = "You Won!"
            return

        elif self.dlrBest > self.usrBest:
            self.result   = "Dealer Wins!"
            return

        else:
            self.result = "Tie!"
            return
        
    def stand_loop(self):
        self.usrSums = self.usrHand.bj_sum()
        while not self.gameover:
            self.dlrHand.append(self.fullDeck.draw_card())
            self.usrSums = self.usrHand.bj_sum()
            self.usrSums = self.usrHand.bj_sum()
            

    def end_game(self, auth: Member):
        if self.usr21 and self.dlr21:
            self.result = "Tie!"
        if self.usrBust:

            # profile = get_profile(self.user)
            # profile["coins"] -= losses
            # profile["craps_record"]["l"] += 1
            # profile["net"]   -= losses
            # set_profile(self.user, profile)

            self.result = f"You Lost! -{self.bet} NickCoin {NC} :regional_indicator_l:"
        if self.dlrBust:
            
            # profile = get_profile(self.user)
            # profile["coins"] -= losses
            # profile["craps_record"]["l"] += 1
            # profile["net"]   -= losses
            # set_profile(self.user, profile)
            
            self.result = f"You Won! +{2*self.bet} NickCoin {NC} :money_mouth:"

    def load_game(self, user: Member):
        #print("[DEBUG]: Loading Game...")

        # get user info
        profile = get_profile(user)
        # get current gamestate
        gameinfo = profile["game"]
        # rebuild game structure
        self.cards.build_from_strs(gameinfo["cards"])
        self.bet = gameinfo["bet"]
        self.usrHand = [Card(i.split("-")[0], int(i.split("-")[1])) for i in gameinfo["usrHand"]]
        self.dlrHand = [Card(i.split("-")[0], int(i.split("-")[1])) for i in gameinfo["dlrHand"]]

    def save_game(self):
        game = {
                "cards": [i.formatted() for i in self.cards.cards],
                "bet":  self.bet,
                "usrHand": [i.formatted() for i in self.usrHand],
                "dlrHand": [i.formatted() for i in self.dlrHand]
                }
        return game

    def get_next(self, msg: Message):

        # set user hand sum as a string
        if self.usrSums[0] == self.usrSums[1] or self.usrSums[1] > 21:
            usrStringSum = str(self.usrSums[0])
        elif self.usrSums[1] == 21:
            usrStringSum = str(self.usrSums[1])
        else:
            usrStringSum = str(self.usrSums[0]) + " or " + str(self.usrSums[1])

        #usrStringSum += f" [DEBUG] - userSums[0]: {self.usrSums[0]}  | userSums[1]: {self.usrSums[1]}"

        # set dealer hand sum as a string
        if self.dlrSums[0] == self.dlrSums[1] or self.dlrSums[1] > 21:
            dlrStringSum = str(self.dlrSums[0])
        elif self.dlrSums[1] == 21:
            dlrStringSum = str(self.dlrSums[1])
        else:
            dlrStringSum = str(self.dlrSums[0]) + " or " + str(self.dlrSums[1])

        #dlrStringSum += f" [DEBUG] - dlrSums[0]: {self.dlrSums[0]}  | dlrSums[1]: {self.dlrSums[1]}"

        # init embeded message
        embed = Embed(title = self.result, 
                      color = Color.red())

        # add dealer hand
        embed.add_field(name="Dealer's Hand:", value = dlrStringSum, inline = False)
        for card in self.dlrHand:
            embed.add_field(name = "▁▁▁▁▁▁▁", value = str(card), inline = True)
        
        if len(self.dlrHand) < 2:
            embed.add_field(name = "▁▁▁▁▁▁▁", value = BLANK_CARD, inline = True)

        # add user hand
        if msg.author.nick == None: name = str(msg.author)
        else:                       name = msg.author.nick

        embed.add_field(name=(name + "'s Hand:"), value = usrStringSum, inline = False)
        for card in self.usrHand:
            embed.add_field(name = "▁▁▁▁▁▁▁", value = str(card), inline = True)

        return embed
