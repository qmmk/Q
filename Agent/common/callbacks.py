import tensorflow as tf
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.logger import TensorBoardOutputFormat


class SummaryWriterCallback(BaseCallback):
    def _on_training_start(self):
        self._log_freq = 1000  # log every 1000 calls

        output_formats = self.logger.Logger.CURRENT.output_formats
        self.tb_formatter = next(
            formatter for formatter in output_formats if isinstance(formatter, TensorBoardOutputFormat))

    def _on_step(self) -> bool:
        if self.n_calls % self._log_freq == 0:
            self.tb_formatter.writer.add_scalars("Prove", {
                "Sicurezza": tf.math.reduce_mean(self.locals["obs_tensor"][0][:, 2]).numpy(),
                "Risorse": tf.math.reduce_mean(self.locals["obs_tensor"][0][:, 3]).numpy(),
                "Tempo": tf.math.reduce_mean(self.locals["obs_tensor"][0][:, 4]).numpy(),
                "Reward": self.locals["rewards"][0]}, self.num_timesteps)
            self.tb_formatter.writer.flush()
