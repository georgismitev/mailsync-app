import unittest

from nose.tools import *
from mailsync.models.adapter import Adapter
from sqlalchemy import *

class TestAdapter(object):

	def setUp(self):
		self.adapter = Adapter()

		self.mysql = {
			"driver": "mysql", 
			"username": "root", 
			"password": "1234", 
			"host": "localhost", 
			"port": 3066, 
			"database": "testdbfortests"
		}

		self.postgresql = {
			"driver": "postgresql", 
			"username": "postgres", 
			"password": "1234", 
			"host": "localhost", 
			"port": 5432, 
			"database": "testdb"
		}

		self.wrong = {
			"driver": "wrongdriver", 
			"username": "root", 
			"password": "1234", 
			"host": "localhost", 
			"port": 3066, 
			"database": "testdb"
		}

	def test_create_connection_string(self):
		# mysql connection string
		eq_(self.adapter.create_connection_string(self.mysql), "mysql://root:1234@localhost:3066/testdbfortests")

		# postgresql connection string
		eq_(self.adapter.create_connection_string(self.postgresql), "postgresql://postgres:1234@localhost:5432/testdb")

	def test_get_engine_valid_parameters(self):
		# mysql connection string
		self.adapter.connection_string = self.adapter.create_connection_string(self.mysql)
		assert self.adapter.get_engine() is not None

		# postgresql connection string
		self.adapter.connection_string = self.adapter.create_connection_string(self.postgresql)
		assert self.adapter.get_engine() is not None
		
		# wrong connection string
		self.adapter.connection_string = self.adapter.create_connection_string(self.wrong)
		assert self.adapter.get_engine() is None

	def test_get_engine_metadata(self):
		# mysql connection string
		self.adapter.connection_string = self.adapter.create_connection_string(self.mysql)
		self.adapter.engine = self.adapter.get_engine()
		assert self.adapter.get_engine_metadata(self.adapter.engine, "reflect=True") is not None

		# wrong connection string
		self.adapter.connection_string = self.adapter.create_connection_string(self.wrong)
		self.adapter.engine = self.adapter.get_engine()
		assert self.adapter.get_engine_metadata(self.adapter.engine, "reflect=True") is None

	def test_is_valid_connection(self):
		# mysql connection string
		self.connect(self.mysql)
		assert self.adapter.engine and self.adapter.metadata

		# postgresql connection string
		self.connect(self.postgresql)
		assert self.adapter.engine and self.adapter.metadata

		# wrong connection string
		self.connect(self.wrong)
		assert not (self.adapter.engine and self.adapter.metadata)

	def connect(self, connection_string):
		self.adapter.connection_string = self.adapter.create_connection_string(connection_string)
		self.adapter.engine = self.adapter.get_engine()
		self.adapter.metadata = self.adapter.get_engine_metadata(self.adapter.engine, "reflect=True")

	def test_get_tables(self):
		self.connect(self.mysql)
		
		tables = self.adapter.get_tables()

		assert(tables is not None)
		assert(len(tables) == 1)
		assert(tables[0] == "user")

	def test_get_columns(self):
		self.connect(self.mysql)

		columns = self.adapter.get_columns("user")

		assert(columns is not None)
		assert(len(columns) == 4)
		assert(columns[0] == "userid")
		assert(columns[1] == "username")
		assert(columns[2] == "email_address")
		assert(columns[3] == "date_created")

	def test_get_rows(self):
		# mysql connection string
		self.connect(self.mysql)
		
		rows = self.adapter.get_top_rows("user")

		assert(rows is not None)
		assert(len(rows) == 3)

		assert(len(rows[0]) == 4)
		assert(len(rows[1]) == 4)
		assert(len(rows[2]) == 4)

		assert(rows[0][0] == 1)
		assert(rows[0][1] == "John")
		assert(rows[0][2] == "john@mail.com")
		assert(rows[0][3] is None)

		assert(rows[1][0] == 2)
		assert(rows[1][1] == "Susan")
		assert(rows[1][2] == "susan@mail.com")
		assert(rows[1][3] is None)

		assert(rows[2][0] == 3)
		assert(rows[2][1] == "Carl")
		assert(rows[2][2] == "carl@mail.com")
		assert(rows[2][3] is None)

	def test_is_primary_key(self):
		self.connect(self.mysql)
		
		table = Table("user", self.adapter.metadata, autoload=True, autoload_with=self.adapter.engine)

		columns = table.columns

		assert(table.columns.has_key("userid") == True)
		assert(self.adapter._is_primary_key(table.columns["userid"]) == True)

		assert(table.columns.has_key("username") == True)
		assert(self.adapter._is_primary_key(table.columns["username"]) == False)

	def test_get_primary_key(self):
		self.connect(self.mysql)
		
		user_table_primary_key = self.adapter.get_primary_key("user")
		
		assert(type(user_table_primary_key) == type("")) 
		assert(user_table_primary_key == "userid")

	def test_get_direction(self):
		direction = self.adapter._get_direction("first")
		assert(direction == asc)

		direction = self.adapter._get_direction("last")
		assert(direction == desc) 

		direction = self.adapter._get_direction("wrong")
		assert(direction == None) 

	def test_get_column_index(self):
		keys = [u'userid', u'username', u'email_address', u'date_created']

		index = self.adapter._get_column_index(keys, "userid")
		assert(index == 0)

		index = self.adapter._get_column_index(keys, "email_address")
		assert(index == 2)
		
		index = self.adapter._get_column_index(keys, "wrong_field")
		assert(index == None)

	def test_get_last_inserted_id(self):
		self.connect(self.mysql)
		table = "user"

		last_inserted_id = self.adapter.get_last_inserted_id(table, "userid", "first")
		assert(last_inserted_id == 1)

		last_inserted_id = self.adapter.get_last_inserted_id(table, "userid", "last")
		assert(last_inserted_id == 22816)
		
		# None, wrongcolumn is not primary key
		last_inserted_id = self.adapter.get_last_inserted_id(table, "username", "last")
		assert(last_inserted_id == None)

		last_inserted_id = self.adapter.get_last_inserted_id(table, "wrongcolumn", "last")
		assert(last_inserted_id == None)

	def test_get_select_query(self):
		columns = {u'first-name': u'username', u'email': u'email_address'}
 		select_query = self.adapter._get_select_query("user", columns, "userid", 1)
 		assert(select_query == "select username as \"first-name\", email_address as \"email\" from user where userid > 1")
 		
		columns = {u'email': u'email_address', u'name': u'username'}
 		select_query = self.adapter._get_select_query("table_name", columns, "id", 991)
 		assert(select_query == "select email_address as \"email\", username as \"name\" from table_name where id > 991")

 	def test_get_rows_to_be_inserted(self):
 		self.connect(self.mysql)
 		table = "user"

 		columns = {u'first-name': u'username', u'email': u'email_address'}
		rows_to_be_inserted = self.adapter.get_rows_to_be_inserted(table, columns, "userid", 1)
		assert(len(rows_to_be_inserted) == 22815)

		columns = {u'email': u'email_address', u'name': u'username'}
		rows_to_be_inserted = self.adapter.get_rows_to_be_inserted(table, columns, "userid", 10000)
		assert(len(rows_to_be_inserted) == 12816)

		columns = {u'email': u'email_address', u'name': u'username'}
		rows_to_be_inserted = self.adapter.get_rows_to_be_inserted(table, columns, "userid", 22816)
		assert(rows_to_be_inserted == [])