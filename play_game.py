from pypokerengine.api.game import setup_config, start_poker

# from subs.bot30.honest_player import HonestPlayer as sub30player
from simple_players.honest_player import HonestPlayer
from simple_players.random_player import RandomPlayer
from simple_players.aggressive_player import AggressivePlayer
from simple_players.caller_player import CallerPlayer
from simple_players.fast_player import FastPlayer
from simple_players.odd_player import OddPlayer
#from pg.pg_player import PgPlayer as current_PgPlayer
from simple_players.honest_players_cpp_like import HonestPlayer as cpp_honest

best_params = [[1.6186857650010011, 1.1986854186890752], [1.0707035587678495, 1.151444829920239], [0.5531481753076868, 0.5401182358645025], [2.7564377633392567, 0.8529146879531582], [0.9336006438927049, 0.7317895265269536], [1.0370427742460506, 1.2812969129151404], 1.2587115770136013, [1.4856281312982338, 0.36498127618075754], [0.7022456554351706, 0.4417983166275421]]

config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)

config.register_player(name="p0", algorithm=FastPlayer(*best_params))
config.register_player(name="p1", algorithm=FastPlayer())
#config.register_player(name="p3", algorithm=cpp_honest())
#config.register_player(name="p4", algorithm=AggressivePlayer())
#config.register_player(name="p6", algorithm=CallerPlayer())
#config.register_player(name="p7", algorithm=RandomPlayer())



summ = 0
num_players = 1
summ_old = [0 for i in range(num_players)]
summ_old_total = [0 for i in range(num_players)]
games_with_0 = 0
num_games = 100
for i in range(num_games):
    game_result = start_poker(config, verbose=0)
    # print(game_result['players'][0]['stack'])#, game_result['players'][3]['stack'], game_result['players'][6]['stack'])
    summ += game_result['players'][0]['stack']
    if game_result['players'][0]['stack'] == 0:
        games_with_0 +=1
    for k in range(num_players):
        summ_old[k] = game_result['players'][k+1]['stack']
        summ_old_total[k] += game_result['players'][k+1]['stack']
    # print(summ/(i+1), 'others', [summ_old[z]/(i+1) for z in range(num_players)], "games with 0 stack:", games_with_0)
    print(game_result['players'][0]['stack'], 'others', [summ_old[z] for z in range(num_players)], "games with 0 stack:", games_with_0)

print(summ/num_games)
print([summ_old_total[i]/num_games for i in range(num_players)])
