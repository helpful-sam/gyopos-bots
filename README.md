# gyopos-bots
 Small bots for the gyopos chat

## Duel Bot
### Project Structure
### /data
#### listening.txt
A temporary log file that works within the scope of each duel. All messages are logged between the initial "/duel" message and the end of the duel. The file is emptied once the duel has completed
#### matches.json
A log of all matches, stored in the following format:
```json
"date": "mmmm dd, yyyy",
"details": "{winner} challenged {loser} and won with a score of {scores[winner]} to {scores[loser]}"
```
#### records.json
A log of user records, stored in the following format:
```json
{
    "user1": {
        "wins": 1,
        "losses": 0,
        "ties": 0
    },
    "user2": {
        "wins": 0,
        "losses": 1,
        "ties": 0
    }
}
```
### /src
#### main.py
initiates the flask application
#### bot-handler.py
handles bot commands
#### duel-logic.py
logic and flow of duels

Important logics:
1. the only person that can say yes or no to continue or abot is the original "/duel" sender, B in the example above
    - achieve this by writing to a temporary "listening.txt" file that will log all messages from the "/duel" message and matching the name of the original "/duel" sender (this file should be emptied, but not deleted after the duel is done or the challenge has expired)
    - the bot will "listen" for 1 minute, after which the bot will stop "listening" and will 1) delete the file, and 2) annouce "The challenge went unanswered for 1 minute, canceling challenge..." 
2. others may text in between the messages, so once the duel has commenced with A and B, only listen to A and B's answer in the flow of the game
3. each round will have a time limit of 1 minute, the round continues until either person submits a right answer
#### data-handler.py
handles read/write operations