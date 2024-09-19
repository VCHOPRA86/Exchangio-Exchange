from flask import session
from flask_login import current_user  # Ensure Flask-Login is imported
from datetime import datetime
import random

# Dummy leaderboard storage
leaderboard = []


class Card:
    def __init__(self, suit, rank):
        """Initialize a card with a suit and rank."""
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        """Return a string representation of the card."""
        return f"{self.rank} of {self.suit}"

class Deck:
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

    def __init__(self):
        """Initialize the deck with 52 cards and shuffle them."""
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.cards)
        self.count = 0  # Initialize card count for card countin


    def deal(self):
        card = self.cards.pop()
        self.update_count(card)  # Update count as cards are dealt
        """Deal one card from the deck."""
        return card    
        
    def update_count(self, card):
        """Update the card count based on the dealt card."""
        if card.rank in ['2', '3', '4', '5', '6']:
            self.count += 1
        elif card.rank in ['10', 'Jack', 'Queen', 'King', 'Ace']:
            self.count -=1

   

class Hand:
    def __init__(self):
        """Initialize an empty hand with no cards, value, or aces."""
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        """Add a card to the hand and update the hand's value."""
        self.cards.append(card)
        if card.rank in ['Jack', 'Queen', 'King']:
            self.value += 10
        elif card.rank == 'Ace':
            self.value += 11
            self.aces += 1
        else:
            self.value += int(card.rank)
        self.adjust_for_ace()

    def adjust_for_ace(self):
        """Adjust the hand's value if it exceeds 21 and contains aces."""
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

class BlackjackGame:
    def __init__(self, db, leaderboard_collection):
        self.db = db
        self.leaderboard_collection = leaderboard_collection
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.deck = Deck()
        self.result = None  # Changed from 0 to None for clarity
        """Initialize the Blackjack game with default values."""
        self.hidden_card = None  # Initialize hidden_card
        self.game_over = False
        self.bet = 0
        self.balance = 1000  # All user accounts start with a £1000 balance
        self.winnings = 0
        self.is_bet_placed = False
        self.is_game_active = False

    def reset_game(self):
        """Reset the game state, including the deck and hands."""
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.game_over = False
        self.result = None  # Changed from 0 to None for clarity
        self.is_bet_placed = False
        self.is_game_active = False  # Ensure this is reset
        self.winnings = 0  # Reset winnings
        self.bet = 0

        # If the balance is <= 0, reset it to £1000
        if self.balance <= 0:
            self.balance = 1000

        # Ensure balance is an integer
        self.balance = int(self.balance)

         # Save the balance to the database
        self.db.users.update_one({"username": current_user.username}, {"$set": {"balance": self.balance}})

            # Reset any game-related variables or session data here
        session['current_bet'] = 0
        session['current_balance'] = 1000  # Reset balance or retrieve from DB
        session['game_in_progress'] = False

    def check_balance(self):
        """Check if the player's balance is 0 or less and end the game if so."""
    


    def new_game(self):
      if self.balance <= 0 and self.bet <=0:
            self.balance = 1000
            

      self.reset_game()  # Reset the game state, like hands and deck 
      self.game_over = False    

      # Save the balance to the database
      self.db.users.update_one({"username": self.username}, {"$set": {"balance": self.balance}})


    def check_blackjack(self, hand):
        """Check if a hand is a Blackjack."""
        if len(hand.cards) == 2:
            # Extract ranks of the cards in the hand
            ranks = [card.rank for card in hand.cards]
             # Check if there's an Ace and a card with a value of 10
            has_ace = 'Ace' in ranks
            has_ten_value_card = any(rank in ranks for rank in ['10', 'Jack', 'Queen', 'King'])
            return has_ace and has_ten_value_card
            print(f"DEBUG - Checking Blackjack: Ranks in hand are {ranks}")  # Debug print
        return False      



    def start_game(self):
        """Start the game if a bet has been placed, deal initial cards, and check balance."""
        if not self.is_bet_placed:
            raise ValueError("You must place a bet first.")
        
            # Check for Blackjack
        player_blackjack = self.check_blackjack(self.player_hand)
        dealer_blackjack = self.check_blackjack(self.dealer_hand)

        if player_blackjack or dealer_blackjack:
            self.check_balance()
    
        # Start the game
        self.is_game_active = True
        self.winnings = 0  # Reset winnings as part of a new game
        self.player_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.hidden_card = self.deck.deal()  # Deal an additional card for the dealer that will be hidden
        
        

    

    def end_game(self, result):


        # Determine if either the player or dealer has a Blackjack
        player_blackjack = self.check_blackjack(self.player_hand)
        dealer_blackjack = self.check_blackjack(self.dealer_hand)

        print(f"DEBUG - Player Blackjack: {player_blackjack}")
        print(f"DEBUG - Dealer Blackjack: {dealer_blackjack}")

        if player_blackjack and dealer_blackjack:
            self.result = "/static/images/results/push.png"
            self.winnings = 0
        elif player_blackjack:
            self.result = "/static/images/results/blackjack.png"
            self.winnings = self.bet * 1.5  # Blackjack typically pays 3:2
        elif dealer_blackjack:
            self.result = "/static/images/results/blackjack.png"
            self.winnings = 0
        else:
            # Proceed with dealer's turn if no blackjack
            self.dealer_turn()

            
            
        """End the game by setting the game state to inactive and updating the leaderboard."""
        # Ensure the game is marked as inactive
        self.is_game_active = False

        # Check the balance before ending the game
        self.check_balance()

        # Update the player's balance in MongoDB
        self.db.users.update_one({"username": current_user.username}, {"$set": {"balance": self.balance}})

        # Insert game data into MongoDB
        self.insert_game_data()


         # Insert the game data into MongoDB
        game_data = {
            "player_name": current_user.username,  # Current logged-in user
            "date": datetime.now(),  # Current date and time
            "result": result,  # e.g., 'Win', 'Lose', 'Tie'
            "winnings": self.winnings  # Retrieve winnings from the game instance
        }

        # Reset the game state if balance <= 0
        if self.balance <= 0:
            self.balance = 1000
            self.db.users.update_one({"username": current_user.username}, {"$set": {"balance": self.balance}})


        # Insert into the 'blackjack' collection (game_collection)
        self.db.blackjack.insert_one(game_data)
        print("Game data inserted:", game_data)


        # Update the leaderboard with the current user's winnings
        result = self.update_leaderboard(current_user.username, self.winnings)
        
        # Update the leaderboard with the current user's winnings
        self.update_leaderboard(current_user.username, self.winnings)  # Ensure leaderboard is updated when game ends
   

    def set_bet(self, amount):
        """Place a bet, ensuring it is valid and within the player's balance."""
        if amount <= 0:
            raise ValueError("Bet amount must be greater than zero.")
        if amount > self.balance:
            raise ValueError("Insufficient balance to place this bet.")
    
        self.bet += amount
        self.balance -= amount
        self.is_bet_placed = True
        self.check_balance()

    def process_result(self):


        player_blackjack = self.check_blackjack(self.player_hand)
        dealer_blackjack = self.check_blackjack(self.dealer_hand)

        print(f"DEBUG - Player Blackjack: {player_blackjack}")
        print(f"DEBUG - Dealer Blackjack: {dealer_blackjack}")

        if player_blackjack and dealer_blackjack:
            self.result = "/static/images/results/push.png"
            self.balance += self.bet
            self.winnings = 0
        elif player_blackjack:
            self.result = "/static/images/results/blackjack.png"
            self.winnings = int(self.bet * 1.5)  # Blackjack typically pays 3:2
            self.balance += self.winnings # Add winnings to balance
        elif dealer_blackjack:
            self.result = "/static/images/results/blackjack-dealer.png"
            self.winnings = 0
        else:
            """Process the result of the game and update the balance and winnings accordingly."""
            if self.result == "/static/images/results/player-wins.png":
                self.winnings += self.bet  # Player wins their bet amount
                self.balance += self.winnings # Add winnings to balance
            elif self.result == "/static/images/results/push.png":
                self.balance += self.bet
                self.winnings = 0  # No additional winnings in case of a push
            elif self.result == "/static/images/results/dealer-busts.png":
                self.winnings += self.bet  # Player wins their bet amount
                self.balance += self.winnings  # Add winnings to balance
            else:
                self.winnings = 0  # Dealer wins or other cases
            
            self.check_balance()  # Ensure balance is updated

         # Ensure balance is an integer
        self.balance = int(self.balance)    


        if self.result in ["/static/images/results/player-wins.png", "/static/images/results/dealer-busts.png"]:
            player_name = current_user.username

    def retrieve_balance(self):
        """Retrieve the player's balance from MongoDB and set it in the game."""
        user = current_user.username  # Get the current logged-in user

        # Fetch the balance from MongoDB for the current user
        user_data = self.db.users.find_one({"username": user}, {"balance": 1})
    
        if user_data and "balance" in user_data:
            self.balance = user_data["balance"]
            print(f"DEBUG - Retrieved balance from DB: {self.balance}")
        else:
            # Set balance to £1000 if the user does not exist in the DB
            self.balance = 1000
            print("DEBUG - No balance found in DB, setting to £1000")

        # Ensure that the balance is at least £1000 if it falls below 0
        if self.balance <= 0:
            self.balance = 1000
            print("DEBUG - Balance was £0 or less, resetting to £1000")        
            

    def update_leaderboard(self, player_name, winnings):
        # Only update the leaderboard with winnings when not a push
        if self.result in ["/static/images/results/player-wins.png", "/static/images/results/dealer-busts.png"]:
            result = self.leaderboard_collection.update_one(
                {'player_name': player_name},
                {'$inc': {'winnings': winnings}},  # Increment winnings
                upsert=True  # Create new entry if player is not in the leaderboard
    )
            return result  # Ensure the result is returned
        else:
        # If result does not require updating the leaderboard, return None
            return None


            result = game.update_leaderboard(player_name, winnings)
        
        if result.upserted_id:
            print(f"New player added with ID: {result.upserted_id}")
        else:
            print(f"Player updated: {player_name}, Matched count: {result.matched_count}")        

    def hit(self):
        if not self.game_over:
            self.player_hand.add_card(self.deck.deal())
            if self.player_hand.value > 21:
                self.result = "/static/images/results/player-busts.png"
                self.game_over = True
                self.process_result()


    def draw_card(self):
        """Draw a card from the deck and return it."""
        if self.deck.cards:
            return self.deck.deal()
        else:
            raise Exception("No more cards in the deck.")
        
    def insert_game_data(self):

        game_data = {
            "player_name": current_user.username,  # Current logged-in user
            "date": datetime.now(),  # Current date and time
            "result": self.result,
            "winnings": self.winnings,  # Retrieve winnings from the game instance
        }
        
        # Insert into the 'blackjack' collection (game_collection)
        self.db.blackjack.insert_one(game_data)
        print("Game data inserted:", game_data)    
        
    def stand(self):
        """Dealer has a chance to 'bluff' and take more risks."""
        bluff_chance = random.random()

        """End the player's turn, play the dealer's hand, and determine the game result."""
        if not self.game_over:
            if self.hidden_card:
                self.dealer_hand.add_card(self.hidden_card)
                self.hidden_card = None

            
            # Dealer bluffs and hits on a higher value based on random chance
            while self.dealer_hand.value < 17 or (self.dealer_hand.value < 19 and bluff_chance > 0.8):
                self.dealer_hand.add_card(self.draw_card())
                self.dealer_hand.adjust_for_ace()
            
            
            
            # Reveal the hidden card
            if self.hidden_card:
                self.dealer_hand.add_card(self.hidden_card)
                self.hidden_card = None


            if self.dealer_hand.value > 21:
                # Dealer busts, player wins
                self.result = "/static/images/results/dealer-busts.png"
                self.winnings = self.bet  # Player wins the amount equal to their bet
            elif self.dealer_hand.value > self.player_hand.value:
                # Dealer wins
                self.winnings = 0
                self.result = "/static/images/results/dealer-wins.png"
            elif self.dealer_hand.value < self.player_hand.value:
                self.result = "/static/images/results/player-wins.png"
                self.winnings = self.bet  # Player wins the amount equal to their bet
                # Player wins
            else:
                # Tie (Push)
                self.result = "/static/images/results/push.png"
                self.winnings = 0
         # Mark game as over and process the result
        self.game_over = True 
        self.process_result()
        
         # Update the leaderboard with the player's name and winnings
        if current_user.is_authenticated:
            player_name = current_user.username
            self.update_leaderboard(player_name, self.winnings)
            self.insert_game_data()

    def get_game_state(self):
        """Return the current game state for rendering."""
        dealer_cards = self.dealer_hand.cards

        # Ensure dealer_cards is always a list
        dealer_cards = dealer_cards or []
        
        # Determine dealer hand images
        if self.is_game_active and not self.game_over:
            # Check if the dealer has at least one card to avoid "list index out of range"
            if len(dealer_cards) > 0:
                dealer_hand_images = [self.card_to_string(dealer_cards[0])] + [self.get_card_back_image()]
            else:
                dealer_hand_images = [self.get_card_back_image()]
        else:
            # If the game is over or not active, show both cards face-up
            dealer_hand_images = [self.card_to_string(card) for card in dealer_cards]

        dealer_value = self.dealer_hand.value if self.is_game_active or self.game_over else None

        # Show player value only when the game is active (i.e., after starting the game)
        player_value = self.player_hand.value if self.is_game_active else None

        player_hand_images = [self.card_to_string(card) for card in self.player_hand.cards]     

        # Debugging output
        print(f"DEBUG - Dealer hand: {self.dealer_hand.cards}")
        print(f"DEBUG - Player hand: {self.player_hand.cards}")
        print(f"DEBUG - Winnings: {self.winnings}")
        print(f"DEBUG - Result: {self.result}")   

        return {
            "player_hand": player_hand_images,
            "dealer_hand": dealer_hand_images,
            "player_value": self.player_hand.value,
            "dealer_value": dealer_value,
            "result": self.result,
            "game_over": self.game_over,
            "bet": self.bet,
            "balance": self.balance,
            "winnings": self.winnings,
            "is_game_active": self.is_game_active,
            "is_bet_placed": self.is_bet_placed
        }

    def card_to_string(self, card):
        """Return the path to the card's image based on its suit and rank."""
        suit = card.suit.lower()  # 'hearts', 'diamonds', 'clubs', 'spades'
        rank = card.rank.lower()  # '2', '3', ..., '10', 'jack', 'queen', 'king', 'ace'
        suit_name = suit[:-1] if suit.endswith('s') else suit  # e.g., 'hearts' to 'heart'
        return f"/static/images/cards/card-{suit_name}-{rank}.png"
    
    def get_card_back_image(self):
        """Return the path to the card back image."""
        return "/static/images/cards/card-back.png"

    def get_card_value(self, card):
        """Return the value of the card based on its rank."""
        if card.rank in ['Jack', 'Queen', 'King']:
            return 10
        elif card.rank == 'Ace':
            return 11
        else:
            return int(card.rank)

   