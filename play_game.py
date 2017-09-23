from pypokerengine.api.game import setup_config, start_poker

# from subs.bot30.honest_player import HonestPlayer as sub30player
from simple_players.honest_player import HonestPlayer
from simple_players.random_player import RandomPlayer
from simple_players.aggressive_player import AggressivePlayer
from simple_players.caller_player import CallerPlayer

config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)
config.register_player(name="p1", algorithm=HonestPlayer())
config.register_player(name="p2", algorithm=HonestPlayer())
config.register_player(name="p3", algorithm=AggressivePlayer())
config.register_player(name="p4", algorithm=AggressivePlayer())
config.register_player(name="p5", algorithm=CallerPlayer())
config.register_player(name="p6", algorithm=CallerPlayer())
config.register_player(name="p7", algorithm=RandomPlayer())
config.register_player(name="p8", algorithm=RandomPlayer())
# config.register_player(name="p7", algorithm=RandomPlayer())
# config.register_player(name="p8", algorithm=RandomPlayer())
# config.register_player(name="p9", algorithm=RandomPlayer())

summ = 0
num_players = 6
summ_old = [0 for i in range(num_players)]
games_with_0 = 0
num_games = 100
for i in range(num_games):
    game_result = start_poker(config, verbose=0)
    # print(game_result['players'][0]['stack'])#, game_result['players'][3]['stack'], game_result['players'][6]['stack'])
    summ += game_result['players'][0]['stack']
    if game_result['players'][0]['stack'] == 0:
        games_with_0 +=1
    for k in range(num_players):
        summ_old[k] += game_result['players'][k+1]['stack']
    print(summ/(i+1), 'others', [summ_old[z]/(i+1) for z in range(num_players)], "games with 0 stack:", games_with_0)

print(summ/num_games)
print([summ_old[i]/num_games for i in range(num_players)])