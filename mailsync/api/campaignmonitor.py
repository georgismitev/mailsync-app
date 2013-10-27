import datetime
import logging

from createsend import *
from mailsync.models.customfield import CustomField

class CampaignMonitor(object):

	def __init__(self, apikey):
		CreateSend.api_key = apikey
		self.provider = CreateSend()

	def get_list_custom_fields(self, listid):
		custom_fields = []

		try:	
			list_custom_fields = List(listid).custom_fields()

			for custom_field in list_custom_fields:
				field = custom_field.FieldName
				
				custom_fields.append(CustomField(field.replace(" ", "-").lower(), field, custom_field.Key))

		except Exception, err:
			logging.error(err)
			custom_fields = []

		return custom_fields

	def get_lists(self):
		client_lists = []
		clients = self.provider.clients()

		for client in clients:
			lists = []
			name = client.Name

			client = Client(client.ClientID)
			for client_list in client.lists():

				lists.append({
					"id": client_list.ListID,
					"name": client_list.Name
				})

			client_lists.append({"client": name, "lists": lists})

		return client_lists

	def prepare(self, users, header_row, column_keys):
		prepared_users = []

		for user in users:
			prepared_user = {}
			prepared_user["CustomFields"] = []

			for i, user_value in enumerate(user):
				header_value = header_row[i].replace("[", "").replace("]", "")
				
				if header_value == "EmailAddress" or header_value == "Name":
					prepared_user[header_value] = user_value
				else:
					if isinstance(user_value, datetime.datetime) or isinstance(user_value, datetime.date):
						encoded_user_value = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
					else:
						encoded_user_value = user_value
					
					prepared_user["CustomFields"].append({
						"Key": header_value,
						"Value": encoded_user_value
					})
			
			prepared_users.append(prepared_user)

		return prepared_users

	def sync_to(self, list_id, header_row, user_chunk, columns):
		try:
			logging.info("list_id: {0}, header_row: {1}, columns: {2}".format(list_id, header_row, columns))

			prepared_users = self.prepare(user_chunk, header_row, columns)

			logging.info("Users prepared: {0}".format(len(prepared_users)))

			subscriber = Subscriber(list_id)

			result = subscriber.import_subscribers(list_id, 
				prepared_users,
				True)
			
			logging.info("DuplicateEmailsInSubmission: {0}".format(result.DuplicateEmailsInSubmission))
			logging.info("FailureDetails: {0}".format(result.FailureDetails))
			logging.info("TotalExistingSubscribers: {0}".format(result.TotalExistingSubscribers))
			logging.info("TotalNewSubscribers: {0}".format(result.TotalNewSubscribers))
			logging.info("TotalUniqueEmailsSubmitted: {0}".format(result.TotalUniqueEmailsSubmitted))

			if result.FailureDetails:
				return True
			else:
				return False
		except Exception, err:
			logging.error(err)
			return False