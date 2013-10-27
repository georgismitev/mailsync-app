import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Date, create_engine, desc, delete
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Index, UniqueConstraint
from mailsync import settings

class SqliteManagement(object):
	
	def __init__(self):
		self.database = settings.SQLITE_PATH
		self.sqlite_mailsync = "sqlite:///" + self.database

		self.engine = create_engine(self.sqlite_mailsync, echo=False)
		self.base = declarative_base(bind=self.engine)
		self.session = scoped_session(sessionmaker(bind=self.engine))

	def create(self):
		self.base.metadata.create_all()

	def commit(self):
		self.session.commit()

sqlite_manager = SqliteManagement()

class Details(sqlite_manager.base):
	__tablename__ = "details"

	_id = Column(Integer, primary_key=True, autoincrement=True)

	last_synced = Column(Integer)
	date_created = Column(Integer)

	__table_args__ = (Index("last_synced_index", "last_synced"), )

	def insert(self, last_synced, date_created):
		new_detail = Details(last_synced=last_synced, date_created=date_created)

		sqlite_manager.session.add(new_detail)
		sqlite_manager.session.commit()

		return new_detail._id

	def get_details(self):
		return sqlite_manager.session.query(Details).order_by(desc(Details.last_synced))

	def find_detail(self, details_id):
		return sqlite_manager.session.query(Details).filter_by(_id=details_id).first()

	def update_last_synced(self, details_id, last_synced):
		sqlite_manager.session.query(Details).filter_by(_id=details_id).update({
			"last_synced": last_synced
		})

		sqlite_manager.session.commit()

	def delete(self, details_id):
		sqlite_manager.session.delete(self.find_detail(details_id))

		sqlite_manager.commit()

class Columns(sqlite_manager.base):
	__tablename__ = "columns"

	_id = Column(Integer, primary_key=True, autoincrement=True)
	column = Column(String)
	value = Column(String)
	tag = Column(String)

	details_id = Column(Integer, ForeignKey("details._id"))
	details = relationship(Details, backref=backref("columns", cascade="all,delete"))
	
	def insert(self, columns, detail_id):
		columns_to_be_inserted = []

		for column in columns:
			columns_to_be_inserted.append(Columns(
				column=column["key"], 
				value=column["value"],
				tag=column["tag"],
				details_id=detail_id))

		sqlite_manager.session.add_all(columns_to_be_inserted)
		sqlite_manager.session.commit()

	def find_details(self, details_id):
		return sqlite_manager.session.query(Columns).filter_by(details_id=details_id).all()

class Database(sqlite_manager.base):
	__tablename__ = "database"

	_id = Column(Integer, primary_key=True, autoincrement=True)
	username = Column(String)
	password = Column(String)
	host = Column(String)
	table = Column(String)
	database = Column(String)
	port = Column(Integer)
	driver = Column(String)

	details_id = Column(Integer, ForeignKey("details._id"))
	details = relationship(Details, backref=backref("database", cascade="all,delete"))

	def insert(self, database, details_id):
		new_database_record = Database(
			username=database["username"],
			password=database["password"],
			host=database["host"],
			table=database["table"],
			database=database["database"],
			port=database["port"],
			driver=database["driver"],
			details_id=details_id)

		sqlite_manager.session.add(new_database_record)
		sqlite_manager.session.commit()

	def find_detail(self, details_id):
		return sqlite_manager.session.query(Database).filter_by(details_id=details_id).first()

class Provider(sqlite_manager.base):
	__tablename__ = "provider"

	_id = Column(Integer, primary_key=True)
	apikey = Column(String)
	provider = Column(String)
	
	details_id = Column(Integer, ForeignKey("details._id"))
	details = relationship(Details, backref=backref("provider", cascade="all,delete"))

	def insert(self, provider, details_id):
		new_provider = Provider(
			apikey=provider["apikey"],
			provider=provider["provider"],
			details_id=details_id)

		sqlite_manager.session.add(new_provider)
		sqlite_manager.session.commit()

	def find_detail(self, details_id):
		return sqlite_manager.session.query(Provider).filter_by(details_id=details_id).first()

	def delete_by_id(self, details_id):
		sqlite_manager.session.query(Provider).filter(details_id=details_id).delete()

class List(sqlite_manager.base):
	__tablename__ = "lists"
	_id = Column(Integer, primary_key=True, autoincrement=True)

	id = Column(String) # provider list id
	name = Column(String)
	status = Column(String)
	last_inserted_id = Column(Integer)
	inserted_rows = Column(Integer)
	rows_to_be_inserted = Column(Integer)

	details_id = Column(Integer, ForeignKey("details._id"))
	details = relationship(Details, backref=backref("lists", cascade="all,delete"))

	def find_detail(self, details_id):
		return sqlite_manager.session.query(List).filter_by(details_id=details_id).first()

	def find_list_by_listid(self, listid):
		return sqlite_manager.session.query(List).filter_by(id=listid).first()

	def insert_basic(self, list_details, details_id):
		new_list = List(
			id=list_details["id"],
			name=list_details["name"],
			details_id=details_id)

		sqlite_manager.session.add(new_list)
		sqlite_manager.session.commit()

	def update_status_completed(self, details_id, last_id):
		sqlite_manager.session.query(List).filter_by(details_id=details_id).update({
			"status": "Completed",
			"last_inserted_id": last_id
		})

		sqlite_manager.session.commit()

	def update_status_running(self, details_id, last_inserted_id, number_of_rows):
		sqlite_manager.session.query(List).filter_by(details_id=details_id).update({
			"status": "Running",
			"last_inserted_id": last_inserted_id,
			"rows_to_be_inserted": number_of_rows,
			"inserted_rows": 0
		})

		sqlite_manager.session.commit()

	def update_inserted_rows(self, details_id, inserted_rows_number):
		sqlite_manager.session.query(List).filter_by(details_id=details_id).update({
			"inserted_rows": List.inserted_rows + inserted_rows_number
		})

		sqlite_manager.session.commit()

class User(sqlite_manager.base):
	__tablename__ = "user"
	_id = Column(Integer, primary_key=True, autoincrement=True)

	username = Column(String)
	password = Column(String)

	username_index = Index("username_index", "username")
	users_index = Index("users_index", "username", "password")

	__table_args__ = (username_index, users_index)

	def users_count(self):
		return sqlite_manager.session.query(User).count()

	def insert(self, username, password):
		new_user = User(username=username, password=password)

		sqlite_manager.session.add(new_user)
		sqlite_manager.session.commit()

	def update_password(self, username, new_password):
		sqlite_manager.session.query(User).filter_by(username=username).update({
			"password": new_password
		})

		sqlite_manager.session.commit()

	def find_user(self, username, password):
		return sqlite_manager.session.query(User).filter(User.username == username).filter(User.password == password).first()

	def find_user_by_username(self, username):
		return sqlite_manager.session.query(User).filter(User.username == username).first()

class Sessions(sqlite_manager.base):
	__tablename__ = "sessions"
	
	session_id = Column(String, primary_key=True)
	expires = Column(Integer)
	data = Column(String)
	user_agent = Column(String)

	session_id_index = Index("session_id_index", "session_id")
	session_id_unique = UniqueConstraint("session_id")

	__table_args__ = (session_id_index, session_id_unique, )

	def find_session_by_session_id(self, session_id):
		return sqlite_manager.session.query(Sessions).filter_by(session_id=session_id).first()

	def insert(self, session_id, expires, data, user_agent):
		new_session = Sessions(session_id=session_id, expires=expires, data=data, user_agent=user_agent)

		sqlite_manager.session.add(new_session)
		sqlite_manager.session.commit()

	def update(self, session_id, expires, data, user_agent):
		sqlite_manager.session.query(Sessions).filter_by(session_id=session_id).update({
			"expires": expires,
			"data": data,
			"user_agent": user_agent
		})

		sqlite_manager.session.commit()

	def upsert(self, session_id, expires, data, user_agent):
		if not self.find_session_by_session_id(session_id):
			self.insert(session_id, expires, data, user_agent)
		else:
			self.update(session_id, expires, data, user_agent)

	def delete_expired(self, time):
		expired_sessions = sqlite_manager.session.query(Sessions).filter_by(expires < time).all()

		for expired_session in expired_sessions:
			sqlite_manager.session.delete(expired_session)
		
		sqlite_manager.session.commit()

	def delete(self, session_id):
		sqlite_manager.session.delete(self.find_session_by_session_id(session_id))
		
		sqlite_manager.session.commit()

sqlite_manager.create()

user_table = User()
database_table = Database()
columns_table = Columns()
provider_table = Provider()
lists_table = List()
details_table = Details()
sessions_table = Sessions()