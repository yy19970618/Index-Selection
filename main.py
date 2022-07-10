from link_database import ManageDB
from RL_brain import QlearningBrain
import time


def update(brain, expected_return_rate):
    for episode in range(10000):
        R = 0  
        while True:
        
            action = brain.choose_action()

         
            return_rate = brain.learn(action)

            R = R + return_rate

            if R > expected_return_rate:
                print(R) 
                break

    # end of game
    print('game over')


if __name__ == "__main__":
 
    manager = ManageDB()
    manager.del_qtable()
    manager.create_qtable()

    brain = QlearningBrain(10, 3, manager)
    update(brain, 0.9)
