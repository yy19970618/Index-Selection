from selection.algorithms.qtable.draw_util import draw_line_chart
from .model import Model
import numpy as np
import random


class QlearningBrain:
    def __init__(self, number, k, manager, inial_cost, learning_rate=0.01, reward_decay=0.98, a=0.4, p=0.5):
        self.lr = learning_rate
        self.gamma = reward_decay  #
        self.a_greedy = a
        self.p_greedy = p
        self.manager = manager

        self.state = "0".ljust(number, '0')
        self.used_bits = number
        self.reserved_bits = k
        self.now_state_cost = inial_cost # manager.getCost(self.state)
        self.limited_indexes = set()
        self.index_width = 2
        self.action_width = 2

        self.model = None
        self.candidate_action = None
        self.cost_history = [self.now_state_cost]

    @staticmethod
    def get_state_changed(state, action):
        #assert len(state) == len(action)
        state_list = list(state)
        action_list = list(action)
        for i in range(len(action_list)):
            if (state_list[-i - 1] == '0' and action_list[-i - 1] == '1') or (
                    state_list[-i - 1] == '1' and action_list[-i - 1] == '0'):
                state_list[-i - 1] = '1'
            else:
                state_list[-i - 1] = '0'
        return ''.join(state_list)


    def setup_constraints(self, limited_indexes, index_width, action_width):
        self.limited_indexes = set(limited_indexes)
        if index_width is not None:
            self.index_width = index_width
        if action_width is not None:
            self.action_width = action_width

    def set_a_greedy(self, a_greedy):
        self.a_greedy = a_greedy

    def set_p_greedy(self, p_greedy):
        self.p_greedy = p_greedy


    def state_change(self, action):
        self.state = QlearningBrain.get_state_changed(self.state, action)
        return self.state


    def get_changed_state(self, action):
        return QlearningBrain.get_state_changed(self.state, action)


    def choose_action(self, predict=False):
        self.manager.check_state_exist(self.state)

        self.model = None
        self.model = Model(self.state, self.action_width)
        self.model.set_db_manager(self.manager)
        self.model.set_used_bits(self.used_bits)
        self.model.set_reserved_bits(self.reserved_bits)
        self.candidate_action = self.model.final(self.limited_indexes, self.index_width, self.action_width)



        rate = np.random.uniform()
        if rate < self.a_greedy or predict:

            got = self.manager.get_maxqvalue(self.state)
            if got[0] != '':
                return got[0]
            elif not predict:
                # 随机选择动作
                return random.choice(self.candidate_action)
        if self.a_greedy <= rate < self.a_greedy + self.p_greedy or predict:

            action_cost = 0 #self.manager.getCost(self.state, action=self.candidate_action[0], relevant=False)
            action = self.candidate_action[0]

            for i in range(1,len(self.candidate_action)):

                #new_state = self.get_changed_state(self.candidate_action[i])
                next_action_cost = self.manager.getCost(self.state, action = self.candidate_action[i], relevant = False)
                # reward 应当是旧cost-新cost，即cost节约量为reward
                #r = old_state_cost - new_state_cost
                if next_action_cost > action_cost:
                        action = self.candidate_action[i]
                        action_cost = next_action_cost
            return action
        else:

            return np.random.choice(self.candidate_action)


    def learn(self, action):
        state_old = self.state
        self.state_change(action)
        self.manager.check_state_exist(self.state)

        new_state_cost = self.manager.getCost(self.state)
        self.cost_history.append(new_state_cost)

        reward = self.now_state_cost - new_state_cost
        self.now_state_cost = new_state_cost


        flag = 0
        if self.manager.check_action_exist(state_old, action):
            q_predict = 0
            flag = 1
        else:
            q_predict = float(self.manager.get_qvalue(state_old, action))

        q_target = reward + self.gamma * float(self.manager.get_maxqvalue(self.state)[1])

        new_value = q_predict + self.lr * (q_target - q_predict)

        if flag == 1:
            self.manager.insert_action(state_old, action, new_value, self.state)
        else:
            self.manager.update_qvalue(state_old, action, new_value)
        if len(self.cost_history) >= 9998:
            print("hello")
        return new_state_cost, new_value


    def predict_best_indexes(self, init_state, epoch=1000):
        self.state = init_state
        self.now_state_cost = self.manager.getCost(self.state)
        cost_history = [self.now_state_cost]
        for _ in range(epoch):
            self.state_change(self.choose_action(predict=True))
            self.now_state_cost = self.manager.getCost(self.state)
            cost_history.append(self.now_state_cost)
        draw_line_chart(cost_history, "./2.png")
        return self.state

    def _model_setup(self, model):
        model.set_used_bits(self.used_bits)
        model.set_reserved_bits(self.reserved_bits)

    def set_used_bits(self, used_bits):
        if used_bits < self.used_bits:
            self.state = self.state[self.used_bits - used_bits:]
        else:
            self.state = '0'.ljust(used_bits - self.used_bits) + self.state
        self.used_bits = used_bits

    def set_reserved_bits(self, reserved_bits):
        self.reserved_bits = reserved_bits
        self.model.set_reserved_bits(reserved_bits)


if __name__ == "__main__":
    s = "0".ljust(10, '0')
    print(s)
    s = s.ljust(12, '0')
    print(s)

    a = ['0', '0', '1', '0', '1']
    print(''.join(a))
