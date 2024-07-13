from flask import Flask, request, jsonify
import os
import json
import random
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

DATA_DIR = "../data/"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")
LISTENING_FILE = os.path.join(DATA_DIR, "listening.txt")

TRIVIA_API_URL = "https://opentdb.com/api.php?amount=3&type=multiple"

# Load questions from JSON or API
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    else:
        try:
            response = requests.get(TRIVIA_API_URL)
            response.raise_for_status()  # Raise an exception for HTTP errors
            questions_data = response.json().get('results', [])
            questions = {}
            for item in questions_data:
                question = item['question']
                correct_answer = item['correct_answer']
                questions[question] = correct_answer
            return questions
        except requests.RequestException as e:
            return {"error": "Error fetching from API, please try again."}


# Load records
def load_records():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

# Load matches
def load_matches():
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Save data
def save_data(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file)

records = load_records()
matches = load_matches()

@app.route('/message', methods=['POST'])
def message():
    data = request.json
    user_id = data['user_id']
    text = data['text'].strip().lower()

    response = ""

    if text.startswith("/duel"):
        if text == "/duel record":
            response = get_duel_record()
        elif text == "/duel matches":
            response = get_duel_matches()
        else:
            challenger = user_id
            challenged = text.split()[1] if len(text.split()) > 1 else None
            response = initiate_duel(challenger, challenged)
    else:
        response = handle_messages(user_id, text)

    return jsonify({"message": response})

def get_duel_record():
    return "\n".join([f"{player} - {record['wins']} wins, {record['losses']} losses, {record['ties']} ties"
                      for player, record in records.items()])

def get_duel_matches():
    return "\n".join([f"{match['date']} - {match['details']}" for match in matches])

def initiate_duel(challenger, challenged):
    if not challenged:
        return "You need to specify whom you want to duel. Usage: /duel @username"
    
    listening_data = {
        "challenger": challenger,
        "challenged": challenged,
        "step": "challenge"
    }
    save_data(LISTENING_FILE, listening_data)
    return f"{challenger} has put forth a challenge! Should you wish to accept, say \"it's on\""

def handle_messages(user_id, text):
    if not os.path.exists(LISTENING_FILE):
        return ""

    with open(LISTENING_FILE, 'r') as file:
        listening_data = json.load(file)

    if listening_data["step"] == "challenge":
        if text == "it's on" and user_id == listening_data["challenged"]:
            listening_data["step"] = "confirmation"
            listening_data["timestamp"] = (datetime.now() + timedelta(minutes=1)).timestamp()
            save_data(LISTENING_FILE, listening_data)
            return f"{user_id} has accepted the duel, to continue, say \"yes\", to abort, say \"no\""

    elif listening_data["step"] == "confirmation" and user_id == listening_data["challenger"]:
        if text == "yes":
            listening_data["step"] = "ready"
            listening_data["questions"] = load_questions()
            save_data(LISTENING_FILE, listening_data)
            return "The duel has commenced! I will provide 3 questions in total with 1 minute each, first to get 2 right wins! Please say \"ready\" for the first question."
        elif text == "no":
            os.remove(LISTENING_FILE)
            return "The duel has been aborted."

    elif listening_data["step"] == "ready":
        if text == "ready" and (user_id == listening_data["challenger"] or user_id == listening_data["challenged"]):
            if "ready_users" not in listening_data:
                listening_data["ready_users"] = []
            listening_data["ready_users"].append(user_id)

            if len(listening_data["ready_users"]) == 2:
                listening_data["step"] = "question"
                listening_data["question_index"] = 0
                listening_data["scores"] = {listening_data["challenger"]: 0, listening_data["challenged"]: 0}
                save_data(LISTENING_FILE, listening_data)
                return ask_question(listening_data)
            else:
                save_data(LISTENING_FILE, listening_data)
                return f"{user_id} is ready. Waiting for the other player."
    
    elif listening_data["step"] == "question":
        if user_id == listening_data["challenger"] or user_id == listening_data["challenged"]:
            question = list(listening_data["questions"].keys())[listening_data["question_index"]]
            answer = listening_data["questions"][question].lower()

            if text == answer:
                listening_data["scores"][user_id] += 1
                save_data(LISTENING_FILE, listening_data)

                if listening_data["scores"][user_id] == 2:
                    winner = user_id
                    loser = listening_data["challenged"] if user_id == listening_data["challenger"] else listening_data["challenger"]
                    update_records(winner, loser)
                    record_match(winner, loser, listening_data["scores"])
                    os.remove(LISTENING_FILE)
                    return f"Ding ding ding! {user_id} got it right! The answer was \"{answer}\"! {user_id} wins the duel!"

                listening_data["question_index"] += 1
                save_data(LISTENING_FILE, listening_data)
                return f"Ding ding ding! {user_id} got it right! The answer was \"{answer}\"!\n\nPlease say \"ready\" for the next question."
            else:
                return f"{user_id}, that's incorrect. Try again."
    
    if datetime.now().timestamp() > listening_data["timestamp"]:
        os.remove(LISTENING_FILE)
        return "The challenge went unanswered for 1 minute, canceling challenge..."

    save_data(LISTENING_FILE, listening_data)
    return ""

def ask_question(listening_data):
    question = list(listening_data["questions"].keys())[listening_data["question_index"]]
    listening_data["timestamp"] = (datetime.now() + timedelta(minutes=1)).timestamp()
    save_data(LISTENING_FILE, listening_data)
    return f"Both players said ready within 1 minute of each other! Here is the first question!\n\n{question}"

def update_records(winner, loser):
    if winner not in records:
        records[winner] = {"wins": 0, "losses": 0, "ties": 0}
    if loser not in records:
        records[loser] = {"wins": 0, "losses": 0, "ties": 0}

    records[winner]["wins"] += 1
    records[loser]["losses"] += 1
    save_data(RECORDS_FILE, records)

def record_match(winner, loser, scores):
    matches.append({
        "date": datetime.now().strftime("%B %d, %Y"),
        "details": f"{winner} challenged {loser} and won with a score of {scores[winner]} to {scores[loser]}"
    })
    save_data(MATCHES_FILE, matches)

if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    app.run(debug=True)
