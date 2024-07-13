from flask import request, jsonify
from main import app
from duel_logic import initiate_duel, handle_messages
from data_handler import load_records, load_matches

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