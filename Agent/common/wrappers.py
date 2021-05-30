from abc import ABC

import numpy as np
from gym import Env, spaces

ILLEGAL_ACTION = -100
TOOLS = 10
LOOKBACK_WINDOW_SIZE = 5


class SystemEnv(Env, ABC):
    def __init__(self):
        super(SystemEnv, self).__init__()

        # STATO --> ACCESO [0], SPENTO [1]
        self.state = spaces.MultiBinary(10)

        # INFO --> STATO - SEC LVL - RES. USAGE - T. EXEC
        self.obs = spaces.Box(low=np.array([0, 0, -10, 0]), high=np.array([1, 10, 10, 180]), shape=(4,),
                              dtype=np.float32)
        self.current_obs = np.zeros((TOOLS, 4))

        # AZIONI --> START [0], STOP [1], WAIT [2]
        self.action_space = spaces.MultiDiscrete([3, 3, 3, 3, 3, 3, 3, 3, 3, 3])

        # SPAZIO DELLE OSSERVAZIONI --> [TOOL ID - STATO - SEC LVL - RES. USAGE - T. EXEC]
        self.observation_space = spaces.Box(low=-10, high=180, shape=(TOOLS, LOOKBACK_WINDOW_SIZE), dtype=np.float32)

    def _next_observation(self):
        frame = np.zeros((TOOLS, LOOKBACK_WINDOW_SIZE))

        # Tool ID
        frame[:, 0] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        for i in range(TOOLS):
            frame[i, 1:5] = self.current_obs[i] = self.obs.sample()

        # Aggiorno lo stato
        frame[:, 1] = self.current_obs[:, 0] = self.state.sample()

        # Sicurezza (indice 2) non ha bisogno di modifiche

        # Normalizzo le risorse
        frame[:, 3] = self.current_obs[:, 2] = (frame[:, 3] + 10) / 2

        # Normalizzo il tempo
        frame[:, 4] = self.current_obs[:, 3] = frame[:, 4] / 18

        return frame

    def step(self, action):
        reward = curr_r = 0

        # Itero per ogni azione e indice di tool
        for idx, x in np.ndenumerate(action):

            stato = self.current_obs[idx][0]
            sicurezza = self.current_obs[idx][1]
            risorse = self.current_obs[idx][2]
            tempo = self.current_obs[idx][3]

            if stato == 0:
                rt = tempo + risorse
                if x == 0:
                    curr_r = ILLEGAL_ACTION
                elif x == 1:
                    # Il tool è attivo e lo si vuole spegnere, buono se ha un impatto rt alto e bassa sicurezza
                    curr_r = pow(1.39, rt) - sicurezza
                else:
                    # Il tool è attivo e lo si vuole lasciare attivo, buono se ha alta sicurezza, degradato da rt
                    curr_r = sicurezza - pow(1.39, rt)
            else:
                if x == 0:
                    # Il tool è spento e lo si vuole accendere, buono se ha impatto sulla sicurezza, degradato da rt
                    curr_r = pow(1.49, sicurezza) - tempo - risorse
                elif x == 1:
                    curr_r = ILLEGAL_ACTION
                else:
                    # Il tool è inattivo e lo si vuole lasciare inattivo, buono con impatto rt alto e bassa sicurezza
                    curr_r = tempo + risorse - pow(1.43, sicurezza)

            reward += curr_r

        obs = np.zeros((TOOLS, LOOKBACK_WINDOW_SIZE))
        obs[:, 0] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        obs[:, 1:5] = self.current_obs

        return obs, reward, True, {}

    def reset(self):
        return self._next_observation()
