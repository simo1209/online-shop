from database import DB
from errors import ApplicationError

class User:
	def __init__(self, email, password, username, address, phone, user_id=None):
		self.id = user_id
		self.email = email
		self.password = password
		self.username = username
		self.address = address
		self.phone = phone

	def to_dict(self):
		user_data = self.__dict__
		del user_data["password"] 
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
		            "SELECT email, password, username, address, phone, id FROM user WHERE id = ?",
		            (user_id,))
		user = result.fetchone()
		if user is None:
		    raise ApplicationError(
		            "User with id {} not found".format(user_id), 404)
		return User(*user)


	@staticmethod
	def all():
		with DB() as db:
		    result = db.execute(
		            "SELECT email, password, username, address, phone, id FROM user").fetchall()
		    return [User(*row) for row in result]
		    
	@staticmethod
	def delete(user_id):
		result = None
		with DB() as db:
		    result = db.execute("DELETE FROM user WHERE id = ?",
		            (user_id,))
		if result.rowcount == 0:
		    raise ApplicationError("No value present", 404)

	def __get_save_query(self):
		query = "{} INTO user {} VALUES {}"
		if self.id == None:
		    args = (self.email, self.password, self.username,  self.adress, self.phone)
		    query = query.format("INSERT", "(email, password, username, address, phone)", args)
		else:
		    args = (self.email, self.password, self.username,  self.adress, self.phone, self.id)
		    query = query.format("REPLACE", "(email, password, username,  address, phone, id)", args)
		return query
