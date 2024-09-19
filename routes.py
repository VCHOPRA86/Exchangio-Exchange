from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime
from blackjack import BlackjackGame
import re
import os


# Load environment variables from .env file
load_dotenv()

# Get the database URI from environment variables
db_uri = os.getenv('MONGO_DB_URI')



# current dateTime
now = datetime.now()



def create_app():
    # Initialize the Flask application
    app = Flask(__name__, static_folder='static')
    app.secret_key = 'your_secret_key'  # Required for session management and flashing messages

    # Ensure `current_user` is available in Jinja templates
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    # Create a MongoClient using the database URI
    client = MongoClient(db_uri)
    db = client.gameData  # Database
    users_collection = db.users  # Collection for user credentials
    game_collection = db.blackjack  # Collection for Blackjack game data
    leaderboard_collection = db.leaderboard  # Collection for leaderboard data

    @app.route('/delete_game_history', methods=['POST'])
    @login_required
    def delete_game_history():
        try:
        # Ensure you are in the correct context
            if not current_user.is_authenticated:
                flash('User must be logged in to delete game history.', 'error')
                return redirect(url_for('dashboard'))

        # Delete all game history for the current user
            result = game_collection.delete_many({'player_name': current_user.username})

            if result.deleted_count > 0:
                flash('All game history has been deleted.', 'success')
            else:
                flash('No game history found to delete.', 'info')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('dashboard'))

 # Testing database 
    #db.blackjack.insert_one({
    #"player_name": "TestUser",
    #"date": datetime.now(),
    #"result": "Win",
    #"winnings": 100
#})

   
    # Testing inserting data into database
   # game_data = {
     #   "_id": ObjectId(),  # Automatically generate an ObjectId if you don't have one
     #   "player_name": "JohnDoe",
     #   "date": datetime(2024, 9, 7, 12, 34, 56),  # Use Python's datetime to represent ISODate
     #   "result": "Win",
    #    "winnings": 200
#}

    # Insert the document
   # insert_result = game_collection.insert_one(game_data)
    
    # Output the result
    #print(f"Inserted document ID: {insert_result.inserted_id}")
    
    # Test MongoDB connection
    try:
        client.admin.command('ping')  # Ping the server to ensure connection is successful
        print("MongoDB connection successful.")
    except errors.ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")

    # Initialize Bcrypt for password hashing
    bcrypt = Bcrypt(app)

    # Initialize Flask-Login for user session management
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'home_route'  # Redirect users to the home view if not authenticated

    # Define the User class for Flask-Login
    class User(UserMixin):
        def __init__(self, id, username, email):
            self.id = id
            self.username = username
            self.email = email

    # Function to load a user from the database based on their ID
    @login_manager.user_loader
    def load_user(user_id):
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(str(user_data['_id']), user_data['username'], user_data['email'])
        return None        

    # Function to verify user credentials
    def verify_user(email, password):
        user = users_collection.find_one({'email': email})
        if user:
            hashed_password = user['password']
            if bcrypt.check_password_hash(hashed_password, password):
                return user  # Return the user data if password matches
        return None
    
    # Function to validate password strength
    def is_valid_password(password):
        # Check for both letters and numbers
        return bool(re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password))

    # Initialize the Blackjack game instance
    game = BlackjackGame(db, db.leaderboard)

    # Route for the home page
    @app.route("/", methods=["GET"])
    def home_route():
        try:
            game_state = game.get_game_state()  # Get the current game state
            print(f"Game State: {game_state}")  # Debugging statement
            return render_template("home.html", game_state=game_state)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return f"An error occurred: {str(e)}", 500
        
    # Route to handle 'hit' action in Blackjack game
    @app.route("/hit", methods=["POST"])
    def hit():
        try:
            game.hit()  # Execute the hit action
        except ValueError as e:
            flash(str(e), 'error')  # Display an error message if something goes wrong
        return redirect(url_for('home_route'))

    # Route to handle 'stand' action in Blackjack game
    @app.route("/stand", methods=["POST"])
    def stand():
        try:
            game.stand()  # Execute the stand action
        except ValueError as e:
            flash(str(e), 'error')  # Display an error message if something goes wrong
        return redirect(url_for('home_route'))
    

    # Route to start a new Blackjack game
    @app.route("/start_game", methods=["POST"])
    @login_required  # Only logged-in users can access this route
    def start_game():
        print(f"User authenticated: {current_user.is_authenticated}")  # Log authentication status
        if not game.is_bet_placed:
            flash("You must place a bet before starting the game.", 'error')  # Inform the user if no bet is placed
        else:
            try:
                game.start_game()  # Start the game
            except ValueError as e:
                flash(str(e), 'error')  # Display an error message if something goes wrong
        return redirect(url_for('home_route'))



    # Route to start a new game
    @app.route("/new_game", methods=["POST"])
    @login_required  # Ensure user is logged in before starting a new game
    def new_game():

        game.reset_game()  # Reset the game state

        game_state = game.get_game_state()  # Get the current game state

        return render_template("home.html", game_state=game_state)
    
    @app.route("/end_game/<string:result>", methods=["POST"])
    @login_required
    def end_game_route(result):
        try:
            game.end_game(result)  # Call the end game logic and pass the result
            flash(f"Game ended with a {result}.", 'success')
            game.save_balance_on_game_end()  # Save the balance to the database
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
        return redirect(url_for('home_route'))

    # Route to set the bet amount in Blackjack game
    @app.route("/set_bet/<int:amount>", methods=["POST"])
    @login_required  # Ensure user is logged in before setting a bet
    def set_bet(amount):
        try:
            game.set_bet(amount)  # Set the bet amount
        except ValueError as e:
            flash(str(e), 'error')  # Display an error message if something goes wrong
        return redirect(url_for('home_route'))

    # Route to display the leaderboard
    @app.route("/leaderboard", methods=["GET"])
    def leaderboard():
        try:
            # Retrieve top 10 players by winnings from MongoDB
            top_players = leaderboard_collection.find().sort('winnings', -1).limit(10)
            top_players_list = list(top_players)  # Convert cursor to list
            print("Retrieved top players:", top_players_list)  # Debugging
            return render_template('leaderboard.html', top_players=top_players_list)
        except Exception as e:
            print(f"An error occurred while fetching leaderboard: {str(e)}")
            return f"An error occurred: {str(e)}", 500

    # Route for the dashboard page
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Fetch game history for the current user from the 'blackjack' collection
        game_history = game_collection.find({'player_name': current_user.username}).sort('date', -1)

    
        # Convert game history cursor to list and format date
        formatted_game_history = [
            {
                '_id': str(game['_id']),  # Convert ObjectId to string
                "date": game['date'].strftime("%d/%m/%Y %H:%M:%S") if isinstance(game['date'], datetime) 
                 else datetime.strptime(game['date'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),  # Handle both datetime and string cases
                'result': game['result'],
                'winnings': game['winnings']
        }
              for game in game_history
              
    ]

    # Fetch leaderboard data from MongoDB
        leaderboard_data = leaderboard_collection.find().sort("winnings", -1)

    # Prepare leaderboard list
        leaderboard = [
        {
            'player_name': player.get('player_name'),
            'winnings': player.get('winnings')
        }
        for player in leaderboard_data
    ]
            
        game_state = game.get_game_state()  # Get the current game state
    # Render the dashboard with both game history and leaderboard
        return render_template('dashboard.html', leaderboard=leaderboard, game_history=formatted_game_history, game_state=game_state)
    

    @app.route('/update_username', methods=['POST'])
    @login_required
    def update_username():
        new_username = request.form['new_username']

        # Validate username length
        if len(new_username) < 5:
            flash('Username must be at least 5 characters long.', 'danger')
            return redirect(url_for('dashboard'))
        

        # Check if the new username is the same as the current username
        if new_username == current_user.username:
            flash(f'Your username is already {current_user.username}', 'danger')
            return redirect(url_for('dashboard'))
            
         # Check if the new username already exists in the database
        if users_collection.find_one({'username': new_username}):
            flash('Username already taken. Please choose a different one.', 'danger')
        # Update user's username in the database
        # db.users.update_one({'_id': current_user.id}, {'$set': {'username': new_username}})
        # Update user's username in the database
        else:
            try:
                 # Update the user's username in the database
                db.users.update_one({'_id': ObjectId(current_user.id)}, {'$set': {'username': new_username}})
                # Logic to update the username
                flash(f'Username successfully changed to {new_username}', 'success')
            except:
                flash(f'Username update failed', 'danger')
            return redirect(url_for('dashboard'))

        
    
    @app.route('/update_password', methods=['POST'])
    @login_required
    def update_password():
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']


        # Check if new passwords match
        if new_password != confirm_new_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Validate the new password
        if not is_valid_password(new_password):
            flash('Password must contain both letters and numbers.', 'danger')
            return redirect(url_for('dashboard'))


        # Fetch the user's current password from the database
        user_data = db.users.find_one({'_id': ObjectId(current_user.id)})

        if not user_data:
            flash('User not found.')
            return redirect(url_for('dashboard'))
        
        # Print for debugging purposes
        print(f"Current hashed password in DB: {user_data['password']}")
        print(f"Entered current password: {current_password}")


         # Verify the current password using bcrypt
        if not bcrypt.check_password_hash(user_data['password'], current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Hash the new password using bcrypt and update in the database
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.users.update_one({'_id': ObjectId(current_user.id)}, {'$set': {'password': new_password_hash}})

        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Route to update a player's score on the leaderboard
    @app.route("/update_score", methods=["POST"])
    @login_required
    def update_score():
        try:
            # Retrieve player name and winnings from the form
            player_name = current_user.username  # Use current_user's username for leaderboard update
            winnings = game.winnings  # Retrieve winnings from the game instance

            # Ensure the game instance is reset for a new game
            game.reset_game()

            # Update leaderboard in MongoDB
            result = leaderboard_collection.update_one(
                {'player_name': player_name},
                {'$inc': {'winnings': winnings}},  # Increment winnings
                upsert=True  # Insert a new document if no matching document is found
            )
            if result.upserted_id:
                print(f"New player added with ID: {result.upserted_id}")
            else:
                print(f"Player updated: {player_name}, Matched count: {result.matched_count}")

            flash(f"Score updated for {player_name}!", 'success')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
        return redirect(url_for('leaderboard'))    

    
    # Route to handle authentication actions (signup, login)
    @app.route("/auth", methods=["POST"])
    def auth():
        action = request.form.get('action')  # Get the action type from the form
        username = request.form.get('username')
        email = request.form.get('email')  # Capture email if using it in signup
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if action == 'signup':
            if len(username) < 5:
                return jsonify({"status": "error", "message": "Username must be at least 5 characters long."})

            if password != confirm_password:
                return jsonify({"status": "error", "message": "Passwords do not match."})

            if not is_valid_password(password):
                return jsonify({"status": "error", "message": "Password must contain both letters and numbers."})    

            if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
                return jsonify({"status": "error", "message": "Username or email already exists."})
        
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user_data = {
                'username': username,
                'email': email,
                'password': hashed_password
            }
            try:
                users_collection.insert_one(user_data)
                print("User data to be inserted:", user_data)
                return jsonify({"status": "success", "message": "Signup successful!"})
            except Exception as e:
                print(f"Error inserting user data: {str(e)}")
                return jsonify({"status": "error", "message": "Failed to insert user data."})

        #try:
           # game_state = game.get_game_state()  # Fetch the current game state
      #  except Exception as e:
           # print(f"An error occurred while fetching game state: {str(e)}")
           # game_state = {}  # Default to empty dict in case of error

        elif action == 'login':
            # Verify user credentials
            user = verify_user(email, password)
        if user:
                user_obj = User(str(user['_id']), user['username'], user['email'])
                login_user(user_obj)  # Log in the user
                session.modified = True  # Mark session as modified to force it to be saved
                print("Session data:", session)  # Debug session contents
                return jsonify({"status": "success", "message": "Login successful!"})
        else:
                return jsonify({"status": "error", "message": "Invalid email or password."})


    # Route to handle user logout
    @app.route("/logout", methods=["POST"])
    @login_required 
    def logout():
        # Call reset game logic
        if 'game_in_progress' in session:
            game.reset_game()  # Ensure this function resets game state, balance, etc.

                # Clear session data
        session.pop('game_in_progress', None)
        session.pop('current_bet', None)
        session.pop('current_balance', None)

        logout_user()  # Log out the user
        flash('You have logged out successfully.')
        return redirect(url_for('home_route'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Run the app in debug mode
