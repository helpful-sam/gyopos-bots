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
handles the commands that call the bot
#### duel-logic.py
logic and flow of duels
#### data-handler.py
handles read/write operations