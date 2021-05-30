import subprocess


def update_tb(filename):
    subprocess.call(['tensorboard ', 'dev ', 'upload ', '--logdir ', 'tensorboard/{}'.format(filename)])
