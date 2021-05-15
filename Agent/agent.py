"""
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory


def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=10, target_model_update=1e-2)
    return dqn


def save_weights(dqn):
    dqn.save_weights("q_weights.h5f", overwrite=True)
    return


def reload_weights(dqn):
    dqn.load_weights("q_weights.h5f")
    return dqn
"""
