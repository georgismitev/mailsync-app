import sys
import time
import threading
import logging

from mailsync.libs.dates import unix_utc_now
from mailsync.models.base import BaseModel
from mailsync.models.adapter import adapter
from mailsync.models.sqlite import details_table, columns_table, database_table, provider_table, lists_table
from mailsync.models.provider import Provider
from mailsync.api.mailchimp import MailChimp
from mailsync.api.campaignmonitor import CampaignMonitor
from mailsync.template import dateformat_local

class Sync(BaseModel):

	def split_rows(self, users, number_of_elements):
		return [users[i:i+number_of_elements] for i in range(0, len(users), number_of_elements)]

	def get_last_id(self, adapter, table, primary_key, list_data):
		# nothing synced for this list
		if not (list_data.last_inserted_id and list_data.status and list_data.inserted_rows and list_data.rows_to_be_inserted):
			last_inserted_id = 0
		elif list_data.last_inserted_id:
			last_inserted_id = list_data.last_inserted_id
		else:
			last_inserted_id = adapter.get_last_inserted_id(table, primary_key, "first")

		return last_inserted_id

	def update_status_running(self, last_inserted_id, number_of_rows, details_id):
		try:
			lists_table.update_status_running(details_id, last_inserted_id, number_of_rows)
			
			return True
		except Exception, err:
			logging.error(err)
			return False

	def update_status_completed(self, last_id, details_id):
		try:
			details_table.update_last_synced(details_id, unix_utc_now())
			
			lists_table.update_status_completed(details_id, last_id)

			return True
		except Exception, err:
			logging.error(err)
			return False

	def sync_users(self, provider, listid, header_row, user_chunks, last_id, details_id, columns):
		try:
			logging.info("sync_users started, provider: {0}, header_row: {1}, last_id: {2}, details_id: {3}".format(provider, header_row, last_id, details_id))
			for user_chunk in user_chunks:
				provider.provider.sync_to(listid, header_row, user_chunk, columns)

				lists_table.update_inserted_rows(details_id, len(user_chunk))

			self.update_status_completed(last_id, details_id)
			return True
		except Exception, err:
			logging.error(err)
			return False	

	def sync_users_thread(self, target, provider, listid, header_row, user_chunks, last_id, details_id, columns):
		sync_thread = threading.Thread(
			target=target, 
			args=(provider, listid, header_row, user_chunks, last_id, details_id, columns))
		sync_thread.daemon = True	
		sync_thread.start()

	def status(self, status, list_data):
		try:
			if list_data.status:
				return str(list_data.status) == status
			
			return False
		except Exception, err:
			logging.error(err)
			return False

	def sync(self, details_id):
		database_data = database_table.find_detail(details_id)
		provider_data = provider_table.find_detail(details_id)
		list_data = lists_table.find_detail(details_id)
		columns_data = columns_table.find_details(details_id)

		adapter.setup(self.get_driver(database_data))

		table = database_data.table
		primary_key = adapter.get_primary_key(table)

		columns = self.get_columns(columns_data)

		if primary_key and adapter.is_valid_connection():
			last_inserted_id = self.get_last_id(adapter, table, primary_key, list_data)
			rows_to_be_inserted = adapter.get_rows_to_be_inserted(table, columns, primary_key, last_inserted_id)
			number_of_rows = len(rows_to_be_inserted)

			if self.status("Completed", list_data) and number_of_rows == 0:
				return True

			provider = Provider(provider_data.provider, provider_data.apikey)
			
			row_chunks = self.split_rows(rows_to_be_inserted, 100)
			header_row = tuple(columns.keys())
			
			self.update_status_running(last_inserted_id, 
				number_of_rows,
				details_id)

			last_id = adapter.get_last_inserted_id(table, 
				primary_key, 
				"last")

			self.sync_users_thread(self.sync_users, 
				provider, 
				list_data.id,
				header_row, 
				row_chunks, 
				last_id, 
				details_id,
				columns)

			return True

		return False

	def sync_status_completed(self, last_synced):
		return {
			"status": "completed",
			"message": "Successfully synced.",
			"progress": 100,
			"last_synced": last_synced
		}

	def sync_status_running(self, inserted_rows, rows_to_be_inserted):
		if rows_to_be_inserted:
			percent = (inserted_rows * 100) / rows_to_be_inserted
		else:
			percent = 0

		return {
			"status": "running",
			"message": "Mailsync is still syncing.",
			"progress": percent,
			"inserted_rows": inserted_rows,
			"rows_to_be_inserted": rows_to_be_inserted
		}

	def sync_status_error(self):
		return {
			"status": "error",
			"message": "An error occured, emails are not successfully synced."
		}

	def sync_status_delete(self, status):
		if status == "Success":
			return {
				"status": "deleted",
				"message": "Sync is successfully removed."
			}
		else: # status == "Error":
			return {
				"status": "error",
				"message": "An error occured, sync is not successfully removed."
			}

	def status_sync(self, details_id):
		sync_status = lists_table.find_detail(details_id)

		try:
			if self.status("Running", sync_status):
				inserted_rows = sync_status.inserted_rows
				rows_to_be_inserted = sync_status.rows_to_be_inserted

				return self.sync_status_running(inserted_rows, rows_to_be_inserted)

			elif self.status("Completed", sync_status):
				last_synced = dateformat_local(details_table.find_detail(details_id).last_synced)

				return self.sync_status_completed(last_synced)
		except Exception, err:
			logging.error(err)
			return self.sync_status_error()

	def _delete(self, details_id):
		details_table.delete(details_id)

	def delete_sync(self, details_id):
		try:
			self._delete(details_id)

			return self.sync_status_delete("Success")
		except Exception, err:
			logging.error(err)
			return self.sync_status_delete("Error")

	def create(self, detail):
		details_id = details_table.insert(detail["last_synced"], detail["date_created"])
		
		columns_table.insert(detail["columns"], details_id)
		database_table.insert(detail["database"], details_id)
		provider_table.insert(detail["provider"], details_id)
		lists_table.insert_basic(detail["list"], details_id)