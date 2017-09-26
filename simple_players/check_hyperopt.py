# best_params = [[1.9242502900271377, 1.4399491425139745], [1.2321173649628636, 0.9673304577212442], [1.8658490587197043, 0.7547097592834577], [2.676391331535975, 1.1787212710926933], [1.243768716573182, 0.4498130177301249], [1.0623347433558077, 1.088574116614371], 1.9480410366569125, [1.0659430651698094, 0.8509603297309563], [0.950456925151415, 0.40586569711277054]]
# best_params = [[1.9481293243008289, 0.4362033658202198], [1.2491870231565032, 0.9416326116942938], [1.3506296313945416, 0.4919079529906567], [0.9466710034156781, 0.5828291485762399], [1.849853264641812, 0.3356119983764777], [0.7148129386973219, 0.964579973742623], 0.714816455840688, [1.099807591650618, 0.6659023279665012], [0.8349211819999771, 0.7112103678281588]]
best_params = [[1.2521060493096905, 1.497640264742834], [1.0259903864006672, 1.0504951109804508], [1.7181167252309422, 0.5717746049552698], [1.599472181259896, 1.1424735705095084], [1.4641806383318614, 0.590615202296598], [0.66999187396324, 1.2881903090245435], 1.957418205433111, [1.7883486156841752, 0.3820177722275549], [0.37728117963524394, 0.452827033154048]]
def print_rules(p1=(1.5, 0.65),
                 p2=(0.6, 0.8),
                 p3=(1, 0.5),
                 p4=(1.5, 0.65),
                 p5=(1, 0.5),
                 p6=(0.6, 0.8),
                 p7=1.5,
                 p8=(1, 0.5),
                 p9=(0.6, 0.8)):
    print("if win_rate >= 0.85 and (round_state['street'] == 'river' or round_state['street'] == 'turn'):\n\
        action = MAX_RAISE\n\
    elif round_state['street'] == 'flop' and self.previous_action == MIN_RAISE and self.previous_street == 'flop':\n\
        action = CALL\n\
    elif round_state['street'] == 'flop' and win_rate >= {} /current_players and valid_actions[1]['amount']/stack < {}:\n\
        action = MIN_RAISE\n\
    elif round_state['street'] == 'flop' and win_rate >= {} and valid_actions[1]['amount']/stack < {}:\n\
        action = CALL\n\
    elif round_state['street'] == 'flop' and win_rate >= {} /current_players and valid_actions[1]['amount']/stack < {}:\n\
        action = CALL\n\
    elif round_state['street'] == 'turn' and self.previous_action == MIN_RAISE and self.previous_street == 'turn':\n\
        action = CALL\n\
    elif round_state['street'] == 'turn' and win_rate >= {} /current_players and valid_actions[1]['amount']/stack < {}:\n\
        action = MIN_RAISE\n\
    elif round_state['street'] == 'turn' and win_rate >= {} /current_players and valid_actions[1]['amount']/stack < {}:\n\
        action = CALL\n\
    elif round_state['street'] == 'turn' and win_rate >= {} and valid_actions[1]['amount']/stack < {}:\n\
        action = CALL\n\
    elif round_state['street'] == 'river' and self.previous_action == MIN_RAISE and self.previous_street == 'river':\n\
        action = CALL\n\
    elif round_state['street'] == 'river' and win_rate >= {} /current_players:\n\
        action = MIN_RAISE\n\
    elif round_state['street'] == 'river' and win_rate >= {} /current_players and valid_actions[1]['amount']/stack < {}:\n\
        action = CALL\n\
    elif round_state['street'] == 'river' and win_rate >= {} and valid_actions[1]['amount']/stack < {}:\n\
        action = CALL\n".format(p1[0],p1[1], p2[0], p2[1], p3[0],p3[1], p4[0], p4[1], p5[0], p5[1], p6[0], p6[1], p7, p8[0], p8[1], p9[0], p9[1]))

print_rules(*best_params)
