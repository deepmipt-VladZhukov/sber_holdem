from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import torch
import torch.nn.functional as F
import torch.optim as optim
from a3c.model import ActorCritic
from torch.autograd import Variable
import numpy as np

gamma = 0.95
NB_SIMULATION = 500
PRINT = False
FIRST_TIME = True

def ensure_shared_grads(model, shared_model):
    for param, shared_param in zip(model.parameters(), shared_model.parameters()):
        if shared_param.grad is not None:
            return
        shared_param._grad = param.grad


class A3Cplayer(BasePokerPlayer):

    FOLD = 0
    CALL = 1
    MIN_RAISE = 2
    MAX_RAISE = 3


    def __init__(self, rank, shared_model, optimizer=None, training = True):
        self.model = ActorCritic()
        self.optimizer = optimizer
        self.model.train()
        self.entropies = []
        self.values = []
        self.log_probs = []
        self.rewards = []
        self.shared_model = shared_model
        self.start_stack = 0
        self.global_stack = 0
        self.random_action = 0
        self.real_action = 0
        self.big_blind_amount = 1
        self.epsilon =1
        self.training = training

    def select_action(self, state):
        value, logit = self.model((Variable(state.unsqueeze(0))))
        prob = F.softmax(logit)
        log_prob = F.log_softmax(logit)
        entropy = -(log_prob * prob).sum(1)
        action = prob.multinomial().data
        log_prob = log_prob.gather(1, Variable(action))
        return action, log_prob, value, entropy

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        current_players = 0
        stack = 0
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
            if i['state'] == 'participating':
                current_players += 1
        if current_players < 2:
            current_players = 2
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=current_players,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        bank = round_state['pot']['main']['amount']
        self.big_blind_amount = 2*round_state['small_blind_amount']

        if valid_actions[2]['amount']['min'] > 0:
            raise_amount = valid_actions[2]['amount']['min'] /self.big_blind_amount
        else :
            raise_amount = valid_actions[1]['amount']/self.big_blind_amount

        action, log_prob, value, entropy = self.select_action(torch.from_numpy(np.array([stack/(10*self.big_blind_amount), bank/self.big_blind_amount,
                                                          valid_actions[1]['amount']/self.big_blind_amount, raise_amount, win_rate / current_players])).float())
        if np.random.random() < self.epsilon:
            action = np.random.randint(4)
            self.random_action += 1
        else :
            action = action.cpu().numpy()
            self.real_action += 1

        self.entropies.append(entropy)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.rewards.append(0)

        if self.FOLD == action:
            if PRINT:
                print("{} fold".format(round_state['street']))
            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif self.CALL == action:
            if PRINT:
                print("{} call {}".format(round_state['street'], valid_actions[1]['amount']))
            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif self.MIN_RAISE == action:
            if PRINT:
                print("{} raise {}".format(round_state['street'], valid_actions[2]['amount']['min']))
            return valid_actions[2]['action'], valid_actions[2]['amount']['min']
        elif self.MAX_RAISE == action:
            if PRINT:
                print("{} allin {}".format(round_state['street'], valid_actions[2]['amount']['max']))
            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
        else:
            raise Exception("Invalid action [ %s ] is set" % action)

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        stack = 0
        for i in game_info['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
        self.global_stack = stack
        self.start_stack = stack

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.model.load_state_dict(self.shared_model.state_dict())

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        global FIRST_TIME
        stack = 0
        # print("round result")
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
        if len(self.rewards) > 0:
            self.rewards[-1] = (stack - self.global_stack)/self.big_blind_amount
            # self.rewards[-1] = max(min(self.rewards[-1], 1), -1)
        self.global_stack = stack
        R = Variable(torch.zeros(1))
        self.values.append(R)
        if self.training:
            gae = torch.zeros(1)
            policy_loss = 0
            value_loss = 0
            for i in reversed(range(len(self.rewards))):
                R = gamma * R + self.rewards[i]
                advantage = R - self.values[i]
                print("r: {} advantage: {} ".format(R.data[0], advantage.data[0]))
                value_loss = value_loss + 0.5 * advantage.pow(2)

                delta_t = self.rewards[i] + gamma * self.values[i + 1].data - self.values[i].data
                gae = gae * gamma + delta_t

                policy_loss = policy_loss - self.log_probs[i] * Variable(gae) - 0.01 * self.entropies[i]

            self.optimizer.zero_grad()
            print("loss",policy_loss + 0.5 * value_loss )
            # if FIRST_TIME:
            #     FIRST_TIME = False
            #     (policy_loss + 0.5 * value_loss).backward(retain_graph=True)
            # else:
            (policy_loss + 0.5 * value_loss).backward()
            torch.nn.utils.clip_grad_norm(self.model.parameters(), 40)

            ensure_shared_grads(self.model, self.shared_model)
            self.optimizer.step()
            self.rewards = []
        else:
            torch.save(self.model.state_dict(), 'weights/model1.pt')