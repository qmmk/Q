from stable_baselines3 import A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from Agent.common.wrappers import SystemEnv
from Agent.common.callbacks import SummaryWriterCallback


class Agent:
    def __init__(self):
        self.env = DummyVecEnv([lambda: SystemEnv()])
        self.model = A2C("MlpPolicy", self.env, verbose=1, tensorboard_log="./tensorboard/")
        return

    def train(self):
        self.model.learn(total_timesteps=25000, callback=SummaryWriterCallback())
        return

    def save(self, filename):
        self.model.save(filename)
        return

    def laod(self, filename):
        self.model = A2C.load(filename)
        return

    def test(self):
        obs = self.env.reset()
        for i in range(200):
            print("OSSERVAZIONE")
            print(obs)
            action, _states = self.model.predict(obs)
            print("ACTION")
            print(action)
            obs, rewards, dones, info = self.env.step(action)
            print("REWARD")
            print(rewards)
            print("----------------\n")
        self.env.close()
        return
