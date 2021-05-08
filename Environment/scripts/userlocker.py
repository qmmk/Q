from tempfile import mkstemp
from shutil import move
from os import remove, chmod
import sys

"""
This is a (very?) horrible way to replicate the command: usermod --lock <username>
It is a "quick and dirty" solution to lock a host user from inside a container
The file /adarch/passwd is a mount of the host file /etc/passwd
"""


# username = sys.argv[1]


def lockuser(username):
    # print("replacing {} in file {}".format(username, source_file_path))
    source_file_path = "./passwd"
    fh, target_file_path = mkstemp()
    with open(target_file_path, 'w') as target_file:
        with open(source_file_path, 'r') as source_file:
            for line in source_file:
                # print(line)
                x = line.split(":")
                if x[0] == username:
                    line = "!" + line
                target_file.write(line)
    # remove(source_file_path)
    move(target_file_path, source_file_path)
    chmod(source_file_path, 644)
