from mailsync.models.adapter import Adapter

class Database(object):

	def __init__(self, connection_details):
		self.connection_details = connection_details

		self.adapter = Adapter()
		self.adapter.setup(self.connection_details)

	def get_tables(self):
		return self.adapter.get_tables()

	def get_columns(self, table):
		return self.adapter.get_columns(table)

	def get_top_rows(self, table):
		return self.adapter.get_top_rows(table)