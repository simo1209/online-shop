from database import DB
from errors import ApplicationError

from auth import AuthUser
from ad import Ad

import time

class User(AuthUser):
	def __init__(self, email, password, username, address, phone, user_id=None, salt = None):
		self.id = user_id
		self.email = email
		if salt is None:
			super().set_and_encrypt_password(password.encode('utf-8'),str(int(time.time())).encode('utf-8'))
		else:
			self.password = password
			self.salt = salt.encode('utf-8')
		self.username = username
		self.address = address
		self.phone = phone

	def to_dict(self):
		user_data = self.__dict__
		del user_data["password"] 
		del user_data["salt"]
		return user_data

	def save(self):
		with DB() as db:
		    cursor = db.execute(self.__get_save_query())
		    self.id = cursor.lastrowid
		return self

	@staticmethod
	def find(user_id):
		result = None
		with DB() as db:
		    result = db.execute(
		            "SELECT email, password, username, address, phone, id, salt FROM user WHERE id = ?",
		            (user_id,))
		user = result.fetchone()
		if user is None:
		    raise ApplicationError(
		            "User with id {} not found".format(user_id), 404)
		return User(*user)

	@staticmethod
	def find_by_username(username):
		result = None
		with DB() as db:
		    result = db.execute(
		            "SELECT email, password, username, address, phone, id, salt FROM user WHERE username = ?",
		            (username,))
		user = result.fetchone()
		if user is None:
		    raise ApplicationError(
		            "User with username {} not found".format(username), 404)
		return User(*user)

	@staticmethod
	def all():
		with DB() as db:
		    result = db.execute(
		            "SELECT email, password, username, address, phone, id, salt FROM user").fetchall()
		    return [User(*row) for row in result]
		    
	@staticmethod
	def delete(user_id):
		result = None
		with DB() as db:
		    result = db.execute("DELETE FROM user WHERE id = ?",
		            (user_id,))
		if result.rowcount == 0:
		    raise ApplicationError("No value present", 404)

	def get_ads(self):
		with DB() as db:
			rows = db.execute('SELECT * FROM ads WHERE active = 0 AND creator_id = ?', (self.id,)).fetchall()
			return [Ad(*row) for row in rows]

	def __get_save_query(self):
		query = "{} INTO user {} VALUES {}"
		if self.id == None:
		    args = (self.email, self.password, self.username,  self.address, self.phone, self.salt.decode('utf-8'))
		    query = query.format("INSERT", "(email, password, username, address, phone, salt)", args)
		else:
		    args = (self.email, self.password, self.username,  self.adress, self.phone, self.id)
		    query = query.format("REPLACE", "(email, password, username,  address, phone, id)", args)
		return query
