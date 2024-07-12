from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Ensure the data directory exists
data_dir = '../data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# File paths
player_records_file = os.path.join(data_dir, 'player_records.json')
match_history_file = os.path.join(data_dir, 'match_history.json')
ongoing_duels_file = os.path.join(data_dir, 'ongoing_duels.json')

# Initialize files if they don't exist
for file in [player_records_file, match_history_file, ongoing_duels_file]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({} if 'ongoing_duels' in file else [], f)

# Trivia API endpoint
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1&type=multiple"

def get_trivia_question():
    response = requests.get(TRIVIA_API_URL)
    if response.status_code == 200:
        data = response.json()
        question_data = data['results'][0]
        question = question_data['question']
        correct_answer = question_data['correct_answer']
        incorrect_answers = question_data['incorrect_answers']
        return question, correct_answer, incorrect_answers
    return None, None, None

def update_records(winner, loser, tie=False):
    with open(player_records_file, 'r') as f:
        player_records = json.load(f)
    
    if winner not in player_records:
        player_records[winner] = {"wins": 0, "losses": 0, "ties": 0}
    if loser not in player_records:
        player_records[loser] = {"wins": 0, "losses": 0, "ties": 0}
    
    if tie:
        player_records[winner]["ties"] += 1
        player_records[loser]["ties"] += 1
    else:
        player_records[winner]["wins"] += 1
        player_records[loser]["losses"] += 1
    
    with open(player_records_file, 'w') as f:
        json.dump(player_records, f)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_message = data.get('message')
    user_id = data.get('user_id')
    
    # Handle user messages and commands
    if user_message.startswith('/duel'):
        parts = user_message.split()
        if len(parts) > 1:
            if parts[1] == 'record':
                return get_records()
            elif parts[1] == 'matches':
                return get_match_history()
            else:
                challenged = parts[1]
                return initiate_duel(user_id, challenged)
    
    with open(ongoing_duels_file, 'r') as f:
        ongoing_duels = json.load(f)
    
    # Check if ongoing duel
    if user_id in ongoing_duels:
        duel = ongoing_duels[user_id]
        return handle_duel_message(duel, user_message, user_id, ongoing_duels)
    
    return jsonify({"message": "Command not recognized."})

def get_records():
    with open(player_records_file, 'r') as f:
        player_records = json.load(f)
    
    records = []
    for player, record in player_records.items():
        records.append(f"{player} - {record['wins']} wins, {record['losses']} losses, {record['ties']} ties")
    return jsonify({"message": "\n".join(records)})

def get_match_history():
    with open(match_history_file, 'r') as f:
        match_history = json.load(f)
    
    matches = []
    for match in match_history:
        matches.append(f"{match['date']} - {match['details']}")
    return jsonify({"message": "\n".join(matches)})

def initiate_duel(challenger, challenged):
    with open(ongoing_duels_file, 'r') as f:
        ongoing_duels = json.load(f)
    
    if challenger in ongoing_duels or challenged in ongoing_duels:
        return jsonify({"message": "One of the players is already in a duel."})
    
    duel = {
        "challenger": challenger,
        "challenged": challenged,
        "state": "awaiting_acceptance",
        "question_index": 0,
        "questions": [],
        "scores": {challenger: 0, challenged: 0}
    }
    ongoing_duels[challenger] = duel
    ongoing_duels[challenged] = duel
    
    with open(ongoing_duels_file, 'w') as f:
        json.dump(ongoing_duels, f)
    
    return jsonify({"message": f"{challenger} has put forth a challenge! {challenged}, to accept, say 'it's on'."})

def handle_duel_message(duel, message, user_id, ongoing_duels):
    if duel["state"] == "awaiting_acceptance" and message.lower() == "it's on":
        if user_id == duel["challenged"]:
            duel["state"] = "awaiting_confirmation"
            with open(ongoing_duels_file, 'w') as f:
                json.dump(ongoing_duels, f)
            return jsonify({"message": f"{duel['challenged']} has accepted the duel. {duel['challenger']}, to confirm, say 'yes'."})
    
    if duel["state"] == "awaiting_confirmation" and message.lower() == "yes":
        if user_id == duel["challenger"]:
            duel["state"] = "awaiting_ready"
            with open(ongoing_duels_file, 'w') as f:
                json.dump(ongoing_duels, f)
            return jsonify({"message": "The duel has commenced! I will provide 3 questions in total. First to get 2 right wins! Please say 'ready' for the first question."})
    
    if duel["state"] == "awaiting_ready" and message.lower() == "ready":
        if user_id in [duel["challenger"], duel["challenged"]]:
            duel.setdefault("ready", []).append(user_id)
            if len(duel["ready"]) == 2:
                duel["ready"] = []
                question, answer, incorrect_answers = get_trivia_question()
                duel["questions"].append({"question": question, "answer": answer, "incorrect_answers": incorrect_answers})
                duel["state"] = "asking_question"
                with open(ongoing_duels_file, 'w') as f:
                    json.dump(ongoing_duels, f)
                return jsonify({"message": f"Here is the first question: {question}"})
    
    if duel["state"] == "asking_question":
        current_question = duel["questions"][-1]
        if message.lower() == current_question["answer"].lower():
            duel["scores"][user_id] += 1
            if duel["scores"][user_id] == 2:
                winner = user_id
                loser = duel["challenged"] if winner == duel["challenger"] else duel["challenger"]
                update_records(winner, loser)
                
                with open(match_history_file, 'r') as f:
                    match_history = json.load(f)
                match_history.append({"date": datetime.now().strftime("%B %d, %Y"), "details": f"{winner} challenged {loser} and won"})
                with open(match_history_file, 'w') as f:
                    json.dump(match_history, f)

                del ongoing_duels[duel["challenger"]]
                del ongoing_duels[duel["challenged"]]
                with open(ongoing_duels_file, 'w') as f:
                    json.dump(ongoing_duels, f)
                return jsonify({"message": f"{winner} wins! {winner}'s record is now {player_records[winner]['wins']} wins, {player_records[winner]['losses']} losses."})
            else:
                duel["state"] = "awaiting_ready"
                with open(ongoing_duels_file, 'w') as f:
                    json.dump(ongoing_duels, f)
                return jsonify({"message": f"{user_id} got it right! The answer was '{current_question['answer']}'. Please say 'ready' for the next question."})
    
    return jsonify({"message": "Invalid state or command."})

@app.route('/save', methods=['POST'])
def save_state():
    # Assuming this endpoint is used for manually triggering state save
    return jsonify({"message": "State is always saved automatically."})

@app.route('/load', methods=['POST'])
def load_state():
    # This function can be used to reload the state from files if needed
    return jsonify({"message": "State loaded successfully."})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
