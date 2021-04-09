from Core import *
from Utilities import *
import random
import subprocess
import os
import os.path
import time
from datetime import datetime, timedelta


N_TENTACTLES = 1

def random_date(start, end, prop):

	stime = start
	etime = end

	ptime = stime + prop * (etime - stime)

	return ptime



def create_table_files(conn):
	create_table_sql =  ''' CREATE TABLE IF NOT EXISTS files (
                                        filename text NOT NULL
                    ); '''
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as e:
		print(e)

def db_insert_file_entry(conn, filename):

	cur = conn.cursor()
	cur.execute('INSERT INTO files VALUES(?)', [filename])
	conn.commit()
	return cur.lastrowid

def crytpolocked_clean(conn):
	cur = conn.cursor()
	cur.execute("SELECT * FROM files")

	rows = cur.fetchall()

	for row in rows:
		if file_exists(row[0]):
			destroy_file(row[0])

	cur = conn.cursor()
	cur.execute('DELETE FROM files')
	conn.commit()

def is_trip_file(conn, filename):
	cur = conn.cursor()
	cur.execute("SELECT * FROM files WHERE filename=?", (filename,))
	if len(cur.fetchall())>0:
		return True
	return False

class Cryptolocked(Core):

	database=r"adarch_persistent/cryptolocked.db"

	def __init__(self, paths):
		super().__init__(paths)

	def initialization(self, paths):

		filenames = {}
		# create a list of random filenames in the given paths
		for path in paths:
			if os.path.isdir(path):
				super().log(Core.DEBUG, "CRYPTOLOCKED" , "will monitor '{}'".format(path))
				for i in range(N_TENTACTLES):
					# why while loop? we do not want to have duplicates in dict, so if duplicate do it again
					while True:
						name = str(hex(random.randint(1,10000))[2:])
						filename = path+'/'+name
						if name not in filenames:
							filenames[name] = filename
							break
			else:
				super().log(Core.ERROR, "CRYPTOLOCKED" , "error, '{}' is not a directory".format(path))

		# DB initialization
		conn = create_connection(self.database)
		if conn is not None:
			create_table_files(conn)
		else:
			super().log(Core.ERROR, "CRYPTOLOCKED" , "error, cannot create the DB connection")

		# Clean previous trip files and DB
		crytpolocked_clean(conn)

		# Place trip files
		for name,filename in filenames.items():
			if file_exists(filename):
				destroy_file(filename)
			content = rand_data()
			create_file(filename, content, None)
			date = random_date( datetime.now()-timedelta(days=120), datetime.now(), random.random())
			modTime = time.mktime(date.timetuple())
			os.utime(filename, (modTime, modTime))
			try:
				subprocess.check_output("auditctl -w {} -p war".format(filename), shell=True)
			except subprocess.CalledProcessError as e:
				super().log(Core.DEBUG, "CRYPTOLOCKED" , "auditctl error: {}".format(e.output))
			db_insert_file_entry(conn, filename)

		super().log(Core.INFO, "CRYPTOLOCKED" , "finished initialization")


	def start(self, mask, name, target):

		if not (mask & Core.IN_ISDIR):

			if (mask & (Core.IN_MODIFY |
						Core.IN_ACCESS |
						Core.IN_CLOSE_WRITE |
						Core.IN_ATTRIB |
						Core.IN_DELETE |
						Core.IN_DELETE_SELF |
						Core.IN_MOVE)):

				conn = create_connection(self.database)
				if conn is None:
					super().log(Core.ERROR, "CRYPTOLOCKED" , "error, cannot create the DB connection")

				filename = str(target+'/'+name)
				if is_trip_file(conn, filename):
						action =""
						if mask & Core.IN_ACCESS:
							action = "ACCESSED"
						if mask & Core.IN_MODIFY:
							action = "MODIFIED"
						if mask & Core.IN_CLOSE_WRITE:
							action = "CLOSED AFTER BEING MODIFIED"
						if (mask & Core.IN_MOVED_TO) or (mask & Core.IN_MOVED_FROM):
							action = "MOVED"
						if (mask & Core.IN_DELETE) or (mask & Core.IN_DELETE_SELF):
							action = "DELETED"
						if mask & Core.IN_ATTRIB:
							action = "subject to an ATTRIBUTE CHANGE"

						audit_info, ppid, comm, user = check_audit(name)
						# TODO: check audit should look for path+name, but for unknown reasons sometimes it doesn't work by providing the entire path

						if self.action & Core.LOG_EVENT:
							super().log(Core.CRITICAL, "CRYPTOLOCKED" , "file '{}/{}' has been {}! {}".format(target, name, action, audit_info))

						if comm != "adarch": #execute action only if the event was not caused by adarch itself
							execute_action(self, "CRYPTOLOCKED", self.action, ppid, user, filename)


	def save_data(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.SAVE_DATA
		self.start(mask, name, target)

	def shutdown_host(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.SHUTDOWN_HOST
		self.start(mask, name, target)

	def kill_pid(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.KILL_PID
		self.start(mask, name, target)

	def kill_user(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.KILL_USER
		self.start(mask, name, target)

	def lock_user(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.LOCK_USER
		self.start(mask, name, target)

	def kill_pid_kill_user(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.KILL_USER | Core.KILL_PID
		self.start(mask, name, target)

	def kill_pid_lock_user(self, mask, name, target):
		self.action = Core.LOG_EVENT | Core.LOCK_USER | Core.KILL_USER | Core.KILL_PID
		self.start(mask, name, target)

	def just_log(self, mask, name, target):
		self.action = Core.LOG_EVENT
		self.start(mask, name, target)