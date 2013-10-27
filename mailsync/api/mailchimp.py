import datetime
import logging

from mailsnake import MailSnake

from mailsync.models.customfield import CustomField

class MailChimp(object):
	
	def __init__(self, apikey):
		self.api_key = apikey

		self.provider = MailSnake(self.api_key)

	def test_connection(self):
		try:
			self.provider.ping()
		except Exception, err:
			logging.error(err)
			return False

		return True

	def get_list_custom_fields(self, listid):
		custom_fields = []
		
		try:
			list_custom_fields = self.provider.listMergeVars(apikey=self.api_key, id=listid)

			for custom_field in list_custom_fields:
				field = custom_field["name"]

				custom_fields.append(CustomField(field.replace(" ", "-").lower(), field, custom_field["tag"]))

		except Exception, err:
			logging.error(err)
			custom_fields = []
			
		return custom_fields

	def get_lists(self):
		lists = []
		mailchimplists = self.provider.lists()

		for mailchimplist in mailchimplists["data"]:

			lists.append({
				"id": mailchimplist["id"],
				"name": mailchimplist["name"]
			})
		
		return [{"client": "", "lists": lists}]

	def prepare(self, users, header_row, column_keys):
		prepared_users = []
		
		for user in users:
			prepared_user = {}
			
			for i, user_value in enumerate(user):
				if isinstance(user_value, datetime.datetime) or isinstance(user_value, datetime.date):
					encoded_user_value = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
				else:
					encoded_user_value = user_value

				prepared_user[header_row[i]] = encoded_user_value
			
			prepared_users.append(prepared_user)

		return prepared_users

	def sync_to(self, list_id, header_row, user_chunk, columns):
		try:
			logging.info("list_id: {0}, header_row: {1}, columns: {2}".format(list_id, header_row, columns))
			
			prepared_users = self.prepare(user_chunk, header_row, columns)
			
			logging.info("Users prepared: {0}".format(len(prepared_users)))
			
			result = self.provider.listBatchSubscribe( 
				id=list_id,
				batch=prepared_users,
				update_existing=True, # ! 
				double_optin=False)

			logging.info(str(result))

			if result["errors"]:
				return True
			else:
				return False
		except Exception, err:
			logging.error(err)
			return False