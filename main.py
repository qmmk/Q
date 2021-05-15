import sys
from Environment.environment import Environment


# from Agent.model import *
# from Agent.agent import *


def main():
    env = Environment()

    # Numero di stati possibili
    # states = env.observation_space.shape[0]

    # Numero di azioni possibili
    # actions = env.action_space.n

    """
    # Modello
    model = build_model(states, actions)
    model.summary()

    # Agente
    dqn = build_agent(model, actions)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])
    dqn.fit(env, nb_steps=50000, visualize=False, verbose=1)

    scores = dqn.test(env, nb_episodes=100, visualize=False)
    print(np.mean(scores.history['episode_reward']))

    _ = dqn.test(env, nb_episodes=15, visualize=True)
    """

    while True:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting\n")
    sys.exit(0)

"""

!pip install tensorflow==2.3.0
!pip install gym
!pip install keras
!pip install keras-rl2

from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random


class Tool():
    def __init__(self, id):
        self.id = id
        self.time_used = 0
        # Ipotesi da valutare -->
        # l'efficacia è in corrispondenza di un determinato attacco
        # il consumo varia anche durante una singola iterazione
        self.efficency = np.random.rand(1)[0] * 10
        self.consumo = np.random.rand(1)[0] * 10


class SystemEnv(Env):
    def __init__(self):
        # Actions we can ADD (tool), REMOVE (tool), WAIT,
        # action UPDATE --> da definire eventuale aggiornarmento della config del tool
        self.action_space = Discrete(3)
        self.tool_space = Discrete(5)

        # Lista di tool disponibili per il sistema
        self.Tools = []
        for n in range(5):
            self.Tools.append(Tool(n))

        self.TotEfficency = 0.0
        self.TotUtilizzo = 0.0
        self.TotConsumo = 0.0

        # Ambiente --> come definire l'ambiente ? Valori di configurazione dei sistemi
        # Ipotesi:
        # ALERT di eventi di sistemi
        # ALERT di eventi di rete
        # Considerare utilizzo CPU, RAM, DISK, BANDA
        # Primo test --> Indice di valori di quanto sia non vulnerabile il sistema
        self.observation_space = Box(low=np.array([0]), high=np.array([100]))

        # Imposto lo stato iniziale
        self.state = 50 + random.randint(-3, 3)

        # Imposto la durata di difesa del sistema
        self.action_length = 60

    def step(self, action, id):
        # Apply action
        # Azione 0 = ADD tool --> tool_space.sample() = random
        if (action == 0):
            print('Aggiungo tool', id)
            self.Tools.append(Tool(id))
        # Azione 1 = REMOVE tool --> valutare perchè è stato rimosso
        if (action == 1):
            print('Rimuovo tool', id)
            # if len(self.Tools) > 0:
            # for n in range(len(self.Tools)):
            #  if(self.Tools[n].id == id):
            #   self.Tools.pop(n)
        # Azione 2 = WAIT --> attendo un eventuale sviluppo
        if (action == 2):
            print('Attendo..')

        # Aggiorno i parametri globali in base all'azione
        for n in range(len(self.Tools)):
            self.Tools[n].time_used += self.Tools[n].time_used + 1
            self.TotEfficency += self.Tools[n].efficency
            self.TotUtilizzo += self.Tools[n].time_used
            self.TotConsumo += self.Tools[n].consumo

            # Aggiorno lo stato attuale
        # Corretto basarsi solo sull'efficienza?
        self.state -= self.TotEfficency

        # Riduco la durata di difesa del sistema
        self.action_length -= 1

        # Calcolo il REWARD
        # Bisogna considerare tutto in un'unica formulazione
        # Considerare anche gli stati precedenti (storia/memory) --> LSTM

        # elif (25 <= self.state <= 35) and (0 <= self.TotConsumo <= 1):
        # reward = 4
        # elif (3 <= self.TotUtilizzo <= 4) and (1 <= self.TotEfficency <= 2):
        # reward = -5

        if np.random.rand(1)[0] > 0.5:
            reward = np.random.rand(1)[0]
        else:
            reward = -1

            # Check if system is done
        if self.action_length <= 0:
            done = True
        else:
            done = False

        # Return step information
        return self.state, reward, done, self.Tools

    def render(self):
        # Implement viz
        pass

    def reset(self):
        self.state = 50 + random.randint(-3, 3)
        return self.state


episodes = 50
for episode in range(1, episodes + 1):
    state = env.reset()
    done = False
    par = False
    tools = []
    score = 0

    while not done:
        # env.render()

        # Scelta importantissima del prossimo tool e azione
        action = env.action_space.sample()
        if action == 1:
            if ()
                while not par:
                    id = env.tool_space.sample()
                    print('ID ', id)
                    for y in range(len(tools)):
                        print('Index', y, 'ID', tools[y].id)
                    par = True
        else:
            id = env.tool_space.sample()

        n_state, reward, done, tools = env.step(action, id)
        score += reward
    print('Episode:{} Score:{}'.format(episode, score))

"""
