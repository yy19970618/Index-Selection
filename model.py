from itertools import combinations

from selection.algorithms.qtable.q_dbmanager import QDBManager
#from selection.algorithms.qtable.RL_brain import QlearningBrain
def get_state_changed(state, action):
  
    state_list = list(state)
    action_list = list(action)
    for i in range(len(action_list)):
        if (state_list[-i - 1] == '0' and action_list[-i - 1] == '1') or (
                state_list[-i - 1] == '1' and action_list[-i - 1] == '0'):
            state_list[-i - 1] = '1'
        else:
            state_list[-i - 1] = '0'
    return ''.join(state_list)

class Model:
    def __init__(self, state, action_width):
        self.state = state
        self.limit_list = set()
        self.action_list = []
        self.action_width = action_width
        self.used_bits = 20
        self.reserved_bits = 10
        self.action_str_list = []
        self.dbmanager = QDBManager()

    def set_db_manager(self, db_manager):
        self.dbmanager = db_manager



    def set_used_bits(self, num):
        if num < self.used_bits:
            self.state = self.state[self.used_bits - num:]
        else:
            self.state = '0'.ljust(num - self.used_bits) + self.state
        self.used_bits = num


    def set_reserved_bits(self, num):
        self.reserved_bits = num


    def make(self):
        index = [i for i in range(0, self.used_bits)]
        for num in range(0, self.action_width + 1):
            for idx in combinations(index, num):
                self.action_list.append(idx)

        for action in self.action_list:
            action_str = ['0'] * self.used_bits
            for act in action:
                action_str[-act - 1] = '1'
            self.action_str_list.append(''.join(action_str))


    def get_limit_list(self, limited_index_list):
        for action in self.action_list:
            for limited_index in limited_index_list:
                if limited_index in action:
                    self.limit_list.add(get_state_changed('0'.ljust(self.used_bits, '0'), action))
                    break


    def got_action(self, state):
        state_copy = state
        state_list = list(state_copy)
        action = []
        for i in range(0, self.action_width):
            if state_list[i] == '1':
                action.append(i)
        return tuple(action)


    def got_index_width(self, state):
        max_width = 0
        indexes = self.dbmanager.str_to_index(state)
        for index in indexes:
            max_width = max(max_width, len(index.columns))
        return max_width


    def got_index_num(self, state):
        state_copy = state
        state_list = list(state_copy)
        w = 0
        for i in range(0, self.action_width):
            if state_list[i] == '1':
                w = w + 1
        return w

    def got_action_width(self, action):
        return self.got_index_width(action)

    def got_action_num(self, action):
        return self.got_index_num(action)


    def storage_limit(self, size):
        for action in self.action_list.copy():
            new_state = get_state_changed(self.state, action)
            indexes = self.dbmanager.str_to_index(new_state)
            storage = 0
            for index in indexes:
                storage += index.estimated_size
                if storage > size:
                    self.action_list.remove(action)
                    break

    def TW_limit(self, index):
        self.get_limit_list(index)
      
        for a in self.action_list.copy():
            if get_state_changed(self.state, a) in self.limit_list:
                self.action_list.remove(a)

    def index_width_limit(self, width):
        for a in self.action_list.copy():
            new_state = get_state_changed(self.state, a)
            if self.got_index_width(new_state) > width:
                self.action_list.remove(a)

    def action_width_limit(self, width):
        for a in self.action_list.copy():
            if len(a) > width:
                self.action_list.remove(a)

  
    def final(self, limited_indexes, index_width, action_width):
        if len(self.action_list) == 0:
            self.make()
        # self.TW_limit(limited_indexes)
        self.index_width_limit(index_width)
        #self.action_width_limit(action_width)
        return self.action_str_list


if __name__ == "__main__":
    # x = {'x': 20, 'a': 12, 'b': 5}
    # y2 = {k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse=True)}
    # print(y2)
    # print(next(iter(y2)))

    # m = Model("10000", 3)
    # m.make()
    # a = m.got_action("01100")
    # print(type(a), a)
    # new = m.change_state("10000", a)
    # print(new)
    #
    # m.get_limit_list(2)
    # print(m.limit_list)
    #
    # w = m.got_index_width("11100")
    # print(w)

    n = Model("10000", 3)
    n.final({2}, 1, 1)
    print(n.action_list)

    n1 = Model("00000", 3)
    n1.final({0}, 2, 1)
    print(n1.action_list)

    n2 = Model("10000", 3)
    n2.final({0, 2}, 1, 2)
    print(n2.action_list)
