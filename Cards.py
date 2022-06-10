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
    cards    = Deck()
    bet      = 0
    
    usrSums  = [0,0]
    usrBest  = 0
    usrHand  = Deck()

    dlrSums  = [0,0]
    dlrBest  = 0
    dlrHand  = Deck()

    gameover = False
    result  = ""

    def __init__(self, msg: Message, bet = 0, init = False, hit = False):
        self.fullDeck    = Deck()
        self.usrHand     = Deck()
        self.dlrHand     = Deck()
        self.usrSums     = [0,0]
        self.usrBest     = 0
        self.dlrSums     = [0,0]
        self.dlrBest     = 0
        self.user        = msg.author
        self.nickname    = get_nickname(self.user)
        self.gameover    = False

        if init:
        # Handle starting a game
            self.bet = bet
            self.fullDeck.new_shuffled_deck()

            self.usrHand.cards.append(self.fullDeck.draw_card())
            self.usrHand.cards.append(self.fullDeck.draw_card())
            self.dlrHand.cards.append(self.fullDeck.draw_card())
            # get current hand sums
            self.usrSums = self.usrHand.bj_sum()
            self.dlrSums = self.dlrHand.bj_sum()
            # get highest numbers
            self.get_best_sums()            
        else:
        # Handle loading a game with a hit / stand
            self.load(self.user)                   # rebuild fields from player JSON
            self.usrSums = self.usrHand.bj_sum()
            self.dlrSums = self.dlrHand.bj_sum()
            
            if hit:                                 # check if player hits or stands
                self.usrHand.cards.append(self.fullDeck.draw_card())
                self.usrSums = self.usrHand.bj_sum()
                self.get_best_sums()                # get highest number
            else: 
                self.stand_loop()
                return
        
        if self.usrBest == 21: 
            self.stand_loop()
        elif self.usrBest > 21:
            self.lose_game()
        elif len(self.usrHand.cards) == 6:
            self.win_game()
        else:
            self.cont_game()

    def get_best_sums(self):
        if self.usrSums[1] < 22: self.usrBest = self.usrSums[1]
        else:                    self.usrBest = self.usrSums[0]

        if self.dlrSums[1] < 22: self.dlrBest = self.dlrSums[1]
        else:                    self.dlrBest = self.dlrSums[0]

    def check_gameover(self):
        self.get_best_sums()
        if self.dlrBest > 21:
            # Check if the dealer busts
            self.win_game()
        elif self.dlrBest > self.usrBest:
            # check if the dealer beat you
            self.lose_game()
        elif self.dlrBest == self.usrBest:
            # check if you and the dealer tie
            self.gameover = True
            self.result   = f"Tie  :triumph: +0 NickCoin {NC}"
        else:
            pass
        
    def stand_loop(self):
        while not self.gameover:
            self.dlrHand.cards.append(self.fullDeck.draw_card())
            self.dlrSums = self.dlrHand.bj_sum()
            self.check_gameover()        

    def win_game(self):
        self.gameover = True
        self.result = f"{self.nickname}, You Won :money_mouth: +{int(self.bet * 1.5)} NickCoin {NC}"
        
        profile = get_profile(self.user)
        profile["coins"] += int(self.bet * 1.5)
        profile["bj_record"]["w"] += 1
        profile["net"]   += int(self.bet * 1.5)
        set_profile(self.user, profile)
            
    def lose_game(self):
        self.gameover = True
        self.result   = f"{self.nickname}, You Lost :regional_indicator_l: -{self.bet} NickCoin {NC}"
        
        profile = get_profile(self.user)
        profile["coins"] -= self.bet
        profile["bj_record"]["l"] += 1
        profile["net"]   -= self.bet
        set_profile(self.user, profile)

    def cont_game(self):
        self.result = ":hearts::diamonds: Hit or Stand?! :diamonds::hearts:"
        set_field(self.user, "game", self.save())
    
    def load(self, user: Member):
        profile = get_profile(user)
        # get current gamestate
        gameinfo = profile["game"]
        # rebuild game structure
        self.fullDeck.build_from_strs(gameinfo["cards"])
        self.bet = gameinfo["bet"]
        self.usrHand.cards = [Card(i.split("-")[0], int(i.split("-")[1])) for i in gameinfo["usrHand"]]
        self.dlrHand.cards = [Card(i.split("-")[0], int(i.split("-")[1])) for i in gameinfo["dlrHand"]]

    def save(self):
        game = {
                "cards"     : [card.formatted() for card in self.fullDeck.cards],
                "bet"       :  self.bet,
                "usrHand"   : [card.formatted() for card in self.usrHand.cards],
                "dlrHand"   : [card.formatted() for card in self.dlrHand.cards]
                }
        return game

    def get_next(self, msg: Message):

        if self.gameover: set_field(msg.author, "game", {})

        # set user hand sum as a string
        if self.usrSums[0] < 22 and self.usrSums[1] < 22 and (self.usrSums[0] != self.usrSums[1]):
            usrStringSum = str(self.usrSums[0]) + " or " + str(self.usrSums[1])
        elif self.usrSums[1] < 22:
            usrStringSum = str(self.usrSums[1])
        else:
            usrStringSum = str(self.usrSums[0])

        # set dealer hand sum as a string
        if self.dlrSums[0] < 22 and self.dlrSums[1] < 22 and (self.dlrSums[0] != self.dlrSums[1]):
            dlrStringSum = str(self.dlrSums[0]) + " or " + str(self.dlrSums[1])
        elif self.dlrSums[1] < 22:
            dlrStringSum = str(self.dlrSums[1])
        else:
            dlrStringSum = str(self.dlrSums[0])

        # init embeded message
        embed = Embed(title = self.result, 
                      color = Color.red())

        # add dealer hand
        embed.add_field(name="Dealer's Hand:", value = dlrStringSum, inline = False)
        for card in self.dlrHand.cards:
            embed.add_field(name = "▁▁▁▁▁▁▁", value = str(card), inline = True)
        if len(self.dlrHand.cards) < 2:
            embed.add_field(name = "▁▁▁▁▁▁▁", value = BLANK_CARD, inline = True)

        # add user hand
        embed.add_field(name=(self.nickname + "'s Hand:"), value = usrStringSum, inline = False)
        for card in self.usrHand.cards:
            embed.add_field(name = "▁▁▁▁▁▁▁", value = str(card), inline = True)

        return embed
