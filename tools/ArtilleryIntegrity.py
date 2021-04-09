from Core import *
from Utilities import *
import subprocess
from os import listdir
from os.path import isfile, join
import os.path




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

def artillery_clean(conn):
	cur = conn.cursor()
	cur.execute('DELETE FROM files')
	conn.commit()

def db_get_file_digest(conn, filename):

	cur = conn.cursor()
	cur.execute("SELECT * FROM files WHERE filename=?", (filename,))

	rows = cur.fetchall()
	if len(rows)>0:
		return rows[0][1]
	return None

def is_monitored_file(conn, filename):
	cur = conn.cursor()
	cur.execute("SELECT * FROM files WHERE filename=?", (filename,))
	if len(cur.fetchall())>0:
		return True
	return False


class ArtilleryIntegrity(Core):

	LOG = 0
	SHUTDOWN_HOST = 1
	KILL_PID = 2
	SAVE_DATA = 3
	action = LOG

	database=r"adarch_persistent/artillery_integrity.db"

	def __init__(self, paths):
		super().__init__(paths)

	def initialization(self, paths):
		# DB initialization
		conn = create_connection(self.database)
		if conn is not None:
			create_table_files(conn)
		else:
			super().log(Core.ERROR, "ARTILLERY INTEGRITY" , "error, cannot create the DB connection")

		# Clean previous associations and DB
		artillery_clean(conn)

		# Create digests for each file in path
		for path in paths:
			if os.path.isdir(path):
				#super().log(Core.INFO, "ARTILLERY INTEGRITY will monitor '{}'".format(path))
				onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
				for name in onlyfiles:
					filename = path + '/' + name
					try:
						subprocess.check_output("auditctl -w {} -p wa".format(filename), shell=True)
					except subprocess.CalledProcessError as e:
						super().log(Core.DEBUG, "ARTILLERY INTEGRITY" , "auditctl error: {} for '{}'".format(e.output, name))
					db_insert_file_entry(conn, filename)
			else:
				super().log(Core.ERROR, "ARTILLERY INTEGRITY" , "error, '{}' is not a directory".format(path))
		super().log(Core.INFO, "ARTILLERY INTEGRITY" , "finished initialization")



	def start(self, mask, name, target):
		#print("Method has been called because of mask: 0x{:8X}".format(mask), name)

		if not (mask & Core.IN_ISDIR): #continue only if the call refers to a file

			if (mask & (Core.IN_MODIFY |
						Core.IN_DELETE |
						Core.IN_DELETE_SELF |
						Core.IN_MOVE|
						Core.IN_ATTRIB|
						Core.IN_CREATE)):

				conn = create_connection(self.database)
				if conn is None:
					super().log(Core.ERROR,"ARTILLERY INTEGRITY" , "error, cannot create the DB connection")

				filename = target+'/'+name

				if is_monitored_file(conn, filename):
					action =""
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

					super().log(Core.CRITICAL, "ARTILLERY INTEGRITY" , "file '{}/{}' has been {}! {}".format(target, name, action, audit_info))
					if comm != "adarch": #execute action only if the event was not caused by adarch itself
						execute_action(self, "ARTILLERY INTEGRITY", self.action, ppid, user, filename)

				if mask & Core.IN_CREATE:
					audit_info, ppid = check_audit(name) #TODO: same as above
					super().log(Core.CRITICAL, "ARTILLERY INTEGRITY" , "file '{}/{}' has been CREATED! {}".format(target, name, audit_info))
					self.execute_action(ppid, filename)

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