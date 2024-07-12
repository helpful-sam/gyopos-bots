Make a kakao bot and have it ask random trivia questions pulled from a trivia question api and make it create a json file with each player and their win count as well as the match history such that it enables two commands:

    "/duel record" outputs:

    B - 2 wins, 1 loss
    A - 1 loss, 1 tie

    "/duel matches" outputs:

    Janaury 4th, 2024 - A challenged B and lost
    February 12th, 2024 - D challenged C and lost

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
    - the only person that can say yes or no to continue or abot is the original "/duel" sender, B in the example above
    - others may text in between the messages, so once the duel has commenced with A and B, only listen to A and B's answer in the flow of the game
    - each round will have a time limit of 1 minute, the round continues until either person submits a right answer

Use python with flask