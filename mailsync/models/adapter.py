import logging

from sqlalchemy import *

from mailsync import settings 

class Adapter(object):

	def setup(self, database={}):
		self.connection_string = self.create_connection_string(database)
		self.engine = self.get_engine()
		self.metadata = self.get_engine_metadata(self.engine, "reflect=True");

	def create_connection_string(self, database):
		return "{0}://{1}:{2}@{3}:{4}/{5}"\
			.format(database["driver"],
				database["username"],
				database["password"],
				database["host"],
				database["port"],
				database["database"])

	def get_engine(self):
		try:
			engine = create_engine(self.connection_string)
		except Exception, err:
			logging.error(err)
			engine = None

		return engine

	def get_engine_metadata(self, engine=None, options=""):
		try:
			metadata = MetaData(engine, options)
		except Exception, err:
			logging.error(err)
			metadata = None 
		
		return metadata

	def is_valid_connection(self):
		return self.engine and self.metadata

	def get_tables(self):
		tables = []

		for table_name in self.metadata.tables:
			tables.append(table_name)

		return tables

	def get_columns(self, table_name=None):
		columns = []
		table = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)

		for column in table.columns:
			columns.append(column.name)

		return columns

	def get_top_rows(self, table_name=None):
		rows = []
		table = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)

		conn = self.engine.connect()
		select_statement = select([table]).limit("3")

		result = conn.execute(select_statement)
		rows = result.fetchall()
		result.close()

		return rows

	def _is_primary_key(self, column):
		return column.primary_key and (isinstance(column.type, INTEGER) or isinstance(column.type, BIGINT))

	def get_primary_key(self, table_name):
		table = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)

		for column in table.columns:
			if self._is_primary_key(column):
				return str(column.key)

		return ""

	def _get_direction(self, order):
		try:
			directions = {
				"first": asc,
				"last": desc
			}

			return directions[order]
		except Exception, err:
			logging.error(err)
			return None

	def _get_column_index(self, keys, primary_key_column):
		try:
			return keys.index(primary_key_column)
		except Exception, err:
			logging.error(err)
			return None

	def get_last_inserted_id(self, table_name, primary_key_column, order):
		direction = self._get_direction(order)
		table = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)
		columns = table.columns

		if not table.columns.has_key(primary_key_column):
			return None

		if not self._is_primary_key(columns.get(primary_key_column)):
			return None

		conn = self.engine.connect()

		select_statement = select([table]).limit("1").order_by(direction(primary_key_column))

		result = conn.execute(select_statement)
		top_row = result.fetchone()
		result.close()
		
		index = self._get_column_index(result.keys(), primary_key_column)

		return top_row[index]

	def _get_select_query(self, table, columns, primary_key, last_id):
		table_columns = list(columns.keys())
		table_columns_list = ", ".join("{0} as \"{1}\"".format(value, key) for key, value in columns.iteritems())

		q = ''
		if self.engine.name != "mysql":
			q = '"'

		query =  "select {0} from {q}{1}{q} where {q}{2}{q} > {3}".format(
			table_columns_list,
			table,
			primary_key,
			last_id,
			q=q)

		return query

	def get_rows_to_be_inserted(self, table, columns, primary_key, last_inserted_id):
		select_query = self._get_select_query(table, columns, primary_key, last_inserted_id)

		return self.engine.execute(select_query).fetchall()

adapter = Adapter()
