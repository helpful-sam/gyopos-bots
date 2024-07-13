import os
import json
import requests

DATA_DIR = "../data/"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=10&type=multiple"

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

def load_records():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def load_matches():
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_data(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file)

def update_records(winner, loser):
    records = load_records()
    if winner not in records:
        records[winner] = {"wins": 0, "losses": 0, "ties": 0}
    if loser not in records:
        records[loser] = {"wins": 0, "losses": 0, "ties": 0}

    records[winner]["wins"] += 1
    records[loser]["losses"] += 1
    save_data(RECORDS_FILE, records)

def record_match(winner, loser, scores):
    matches = load_matches()
    matches.append({
        "date": datetime.now().strftime("%B %d, %Y"),
        "details": f"{winner} challenged {loser} and won with a score of {scores[winner]} to {scores[loser]}"
    })
    save_data(MATCHES_FILE, matches)
