Make a kakao bot and have it ask random trivia questions pulled from a file called questions.json (or, if it doesn't exist, pull from a trivia question api) and make it create a json file with each player and their win count as well as the match history such that it enables two commands:

    "/duel record" outputs:

    B - 2 wins, 1 loss
    A - 1 loss, 1 tie

    "/duel matches" outputs:

    Janaury 4th, 2024 - A challenged B and lost
    February 12th, 2024 - D challenged C and lost


The format of the questions.json is as follows, and the bot should look for captial insensitive answers to match to the json file:

{
    "question 1": "answer",
    "question 2": "answer",
    "question 3": "answer"
}


The format of the duel should be as follows:

    A: *says something*
    B: /duel
    Bot: B has put forth a challenge! Should you wish to accept, say "it's on"
    A: it's on
    Bot: A has accepted the duel, to continue, say "yes", to abort, so "no"
    B: yes
    Bot: The duel has commenced! I will provide 3 questions in total with 1 minute each, first to get 2 right wins! Please say "ready" for the first question.
    B: ready
    A: ready
    Bot: Both players said ready within 1 minute of each other! Here is the first question!
    Bot: *question 1*
    A: *wrong answer*
    B: *wrong answer*
    B: *right answer*
    Bot: Ding ding ding! B got it right! The answer was "answer"!
    Bot: Please say "ready" for the second question.
    ....
    Bot: Please say "ready" for the third and final question.
    ....
    Bot: B wins! B's record is 2 wins, 1 loss


Important logics:
    1. the only person that can say yes or no to continue or abot is the original "/duel" sender, B in the example above
        - achieve this by writing to a temporary "listening.txt" file that will log all messages from the "/duel" message and matching the name of the original "/duel" sender (this file should be emptied, but not deleted after the duel is done or the challenge has expired)
        - the bot will "listen" for 1 minute, after which the bot will stop "listening" and will 1) delete the file, and 2) annouce "The challenge went unanswered for 1 minute, canceling challenge..." 
    2. others may text in between the messages, so once the duel has commenced with A and B, only listen to A and B's answer in the flow of the game
    3. each round will have a time limit of 1 minute, the round continues until either person submits a right answer
    4. all json/txt files will be stored in the relative directory "../data/"

Use python with flask