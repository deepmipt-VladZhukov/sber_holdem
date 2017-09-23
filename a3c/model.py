import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

def normalized_columns_initializer(weights, std=1.0):
    out = torch.randn(weights.size())
    out *= std / torch.sqrt(np.square(out).sum(0, True))
    return out


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Linear') != -1:
        weight_shape = list(m.weight.data.size())
        fan_in = weight_shape[1]
        fan_out = weight_shape[0]
        w_bound = np.sqrt(6. / (fan_in + fan_out))
        m.weight.data.uniform_(-w_bound, w_bound)
        m.bias.data.fill_(0)


class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.layer1 = nn.Linear(5, 32)
        self.layer2 = nn.Linear(32, 32)

        self.critic_linear = nn.Linear(32, 1)
        self.actor_linear = nn.Linear(32, 4)

        self.apply(weights_init)
        # self.actor_linear.weight.data = normalized_columns_initializer(self.actor_linear.weight.data, 0.01)
        self.actor_linear.bias.data.fill_(0)

        # self.critic_linear.weight.data = normalized_columns_initializer(self.critic_linear.weight.data, 1.0)
        self.critic_linear.bias.data.fill_(0)

        self.train()

    def forward(self, inputs):
        x = F.elu(self.layer1(inputs))
        x = F.elu(self.layer2(x))

        return self.critic_linear(x), self.actor_linear(x)
