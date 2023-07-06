from flask import Flask, render_template, request
from pymongo import MongoClient
import time

#from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

uri = "mongodb+srv://jjames71396:qUFaF5pYhmjxAxPD@cluster0.ldooqi5.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

client.db.command("dropDatabase")

db = client['game_db']
collection = db['game_states']


# Game parameters
pile_sizes = [0, 0, 0]
min_pickup = 1
max_pickup = 3
players = {}


document = {'name': 'game_state','started': False,'p1': '','p2': '','question': '', 'p1s': 0, 'p2s': 0}
inserted_document = collection.update_one({'name':'game_state'},{'$set': document})

@app.route('/')
def index():
    query = {"name": "game_state"} 
    game_state = collection.find_one(query)
    # Retrieve the game state from the database
    print(game_state)
    turn = None
    cur_player = None
    p = players
    start = False
    if game_state["question"] == '':
        game_state = None
        start = True
  
            
        
    # Render the template with the game state and player names
    return render_template('index.html', start=start, time=str(time.time()), game_state=game_state)

@app.route('/players', methods=['POST'])
def players():
    query = {"name": "game_state"} 
    game_state = collection.find_one(query)
    if game_state['p1'] == '':
        player1 = request.form['player1']
        player2 = None
    elif game_state['p2'] == '':
        player1 = None
        player2 = request.form['player2']
    
    if player1 is not None and player1 != '':
        document = {'p1': player1}
        inserted_document = collection.update_one(query,{'$set': document})
    elif player2 is not None and player2 != '':
        document = {'p2': player2}
        inserted_document = collection.update_one(query,{'$set': document})
    # Redirect back to the index page
    return index()

@app.route('/pick', methods=['POST'])
def pick():
    query = {"name": "game_state"} 
    game_state = collection.find_one(query)
    pile_number = int(request.form['pile_number']) - 1
    num_stones = int(request.form['num_stones'])
    if pile_number < 0:
        pile_number = 0
    elif pile_number > 2:
        pile_number = 2
    # Update the game state
    pile_sizes[pile_number] -= num_stones
    players[game_state['turn']] += num_stones
    
    # Save the updated game state to the database
    collection.update_one(query, {'$set': {'pile_sizes': pile_sizes}})
    # Switch players
    if game_state['turn'] == 1:
        document = {'turn': 2}
        
    else:
        document = {'turn': 1}
    inserted_document = collection.update_one(query,{'$set': document})
    
    # Redirect back to the index page
    return index()

@app.route('/restart', methods=['POST'])
def restart():
    global players
    query = {"name": "game_state"} 
    document = {'name': 'game_state','started': False,'p1': '','p2': '','question': '', 'p1s': 0, 'p2s': 0}
    inserted_document = collection.update_one({'name':'game_state'},{'$set': document})
    players = {
        1: 0,
        2: 0
    }

    return index()

@app.route('/start', methods=['POST'])
def start():
    global players
    query = {"name": "game_state"} 
    game_state = collection.find_one(query)
    # Retrieve the game parameters from the form
    question = request.form['name']
    p1 = int(request.form['pile1'])
    p2 = int(request.form['pile2'])
    players = {
        1: p1,
        2: p2
    }

    # Save the initial game state to the database
    collection.update_one(query, {'$set': {'question': question, 'p1s': p1, 'p2s': p2, 'started': True}})
    # Redirect back to the index page
    return index()


if __name__ == '__main__':
    app.run(debug=True)