import unittest

from nose.tools import *
from sqlalchemy import *
from bson.objectid import ObjectId

from randomdomain.libs.mongodb import mongo_backend
from randomdomain.libs.dates import unix_utc_now
from mailsync.models.sync import Sync
from mailsync.models.adapter import Adapter
from mailsync.api.mailchimp import MailChimp
from mailsync.api.campaignmonitor import CampaignMonitor

class TestSync(object):

	def setUp(self):
		self.id = "5073d616dd0ef409aaaaeeec0fee"

		self.mysql = {
			"driver": "mysql", 
			"username": "root", 
			"password": "1234", 
			"host": "localhost", 
			"port": 3066, 
			"database": "testdbfortests"
		}

		self.adapter = Adapter()
		self.adapter.setup(self.mysql)

		self.details = mongo_backend.get_collection("details")
		self.detail = self.details.find_one({"_id": ObjectId(self.id)})
		self.sync = Sync(self.id)

	def test_split_rows(self):
		chunks = self.sync.split_rows(range(1005), 10)
		chunks_len = len(chunks)

		assert(chunks_len == 101)

		for index, chunk in enumerate(chunks):
			if index < (chunks_len - 1):
				assert(len(chunk) == 10)
			else:
				assert(len(chunk) == 5)

		chunks = self.sync.split_rows(range(0), 10)
		chunks_len = len(chunks)
		assert(chunks_len == 0)

		chunks = self.sync.split_rows(range(5), 10)
		chunks_len = len(chunks)
		assert(chunks_len == 1)
		assert(len(chunks[0]) == 5)

	def test_get_last_inserted_id(self):
		last_inserted_id = self.sync.get_last_inserted_id(self.detail["list"])
		assert(last_inserted_id == 22816)

		last_inserted_id = self.sync.get_last_inserted_id({})
		assert(last_inserted_id == None)

		last_inserted_id = self.sync.get_last_inserted_id({"status":{}})
		assert(last_inserted_id == None)

	def test_get_last_id(self):
		last_id = self.sync.get_last_id(self.adapter, "user", "userid", self.detail["list"])
		assert(last_id == 22816)
		
		last_id = self.sync.get_last_id(self.adapter, "user", "userid", {})
		assert(last_id == 1)

	def test_update_status_running(self):
		# setup
		statebefore = self.detail
		last_inserted_id = 1234
		rows_to_be_inserted = 5678

		assert(self.sync.update_status_running(last_inserted_id, rows_to_be_inserted) == True)
		detail = self.details.find_one({"_id": ObjectId(self.id)})

		assert(detail["list"]["status"]["status"] == "Running")
		assert(detail["list"]["status"]["last_inserted_id"] == last_inserted_id)
		assert(detail["list"]["status"]["rows_to_be_inserted"] == rows_to_be_inserted)
		assert(detail["list"]["status"]["inserted_rows"] == 0)

		# tear down
		self.detail = statebefore
		self.details.save(statebefore)
		self.details.ensure_index("_id")

	def test_update_status_completed(self):
		# setup
		statebefore = self.detail
		last_id = 1234

		assert(self.sync.update_status_completed(last_id) == True)
		detail = self.details.find_one({"_id": ObjectId(self.id)})

		assert(detail["list"]["status"]["status"] == "Completed")
		assert(detail["list"]["status"]["last_inserted_id"] == last_id)

		# tear down
		self.detail = statebefore
		self.details.save(statebefore)
		self.details.ensure_index("_id")

	def test_sync_users(self):
		# setup
		statebefore = self.detail

		campaignmonitor = CampaignMonitor("787e70d714cdce3178610ddde2d7da08deeeeeddddd")
		campaignmonitor_list_id = "fl8b40a4d15de4e7d83ead7e6b839544ib"

		header_row = tuple(self.detail["columns"].keys())
		user_chunks = [[('John', 'john@randomdomain.li'), ('Susan', 'susan@randomdomain.li'), ('Carl', 'carl@randomdomain.li')]]
		
		assert(self.sync.sync_users(campaignmonitor, campaignmonitor_list_id, header_row, user_chunks, 22816) == True)

		detail = self.details.find_one({"_id": ObjectId(self.id)})
		assert(detail["list"]["status"]["inserted_rows"] == statebefore["list"]["status"]["inserted_rows"] + 3)
		
		# teardown
		self.details.save(statebefore)
		self.details.ensure_index("_id")

	def test_get_provider(self):
		provider = self.sync.get_provider(self.detail["provider"], "apikey")
		assert(provider is not None)
		assert(isinstance(provider, CampaignMonitor))

		# mocking provider data
		provider_data = {}
		provider_data["provider"] = "mailchimp"

		provider = self.sync.get_provider(provider_data, "apikey")
		assert(provider is not None)
		assert(isinstance(provider, MailChimp))

	def test_status(self):
		list_data = self.detail["list"]

		status = self.sync.status("Completed", list_data)
		assert(status == True)

		status = self.sync.status("Completed", {})
		assert(status == False)

		rdetail = self.details.find_one({"_id": ObjectId("5073d5f0dd0ef409aaec0fed")})

		status = self.sync.status("Completed", rdetail["list"])
		assert(status == False)

	def test_sync_status_completed(self):
		time = unix_utc_now()

		status = {
			"status": "completed",
			"message": "Successfully synced.",
			"progress": 100,
			"last_synced": time
		}

		assert(self.sync.sync_status_completed(time) == status)

	def test_sync_status_running(self):
		inserted_rows = 1234
		rows_to_be_inserted = 5678

		status = {
			"status": "running",
			"message": "Mailsync is still syncing.",
			"progress": (inserted_rows * 100) / rows_to_be_inserted,
			"inserted_rows": inserted_rows,
			"rows_to_be_inserted": rows_to_be_inserted
		}

		rows_to_be_inserted = 0

		status = {
			"status": "running",
			"message": "Mailsync is still syncing.",
			"progress": 0,
			"inserted_rows": inserted_rows,
			"rows_to_be_inserted": rows_to_be_inserted
		}

		assert(self.sync.sync_status_running(inserted_rows, rows_to_be_inserted) == status)

	def test_sync_status_error(self):
		status = {
			"status": "error",
			"message": "An error occured, emails are not successfully synced."
		}

		assert(self.sync.sync_status_error() == status)

	def test_sync_status_delete(self):
		success_status = {
			"status": "deleted",
			"message": "Sync is successfully removed."
		}

		assert(self.sync.sync_status_delete("Success") == success_status)

		error_status = {
			"status": "error",
			"message": "An error occured, sync is not successfully removed."
		}

		assert(self.sync.sync_status_delete("Error") == error_status)
		assert(self.sync.sync_status_delete("Wrong") == error_status)

	def test_delete(self):
		# setup
		statebefore = self.detail
		
		self.sync._delete()
		detail = self.details.find_one({"_id": ObjectId(self.id)})
		assert(detail == None)

		# teardown
		self.details.save(statebefore)
		self.details.ensure_index("_id")

	def test_delete_sync(self):
		# setup
		statebefore = self.detail

		result = self.sync.delete_sync()

		detail = self.details.find_one({"_id": ObjectId(self.id)})
		assert(detail == None)

		success_status = {
			"status": "deleted",
			"message": "Sync is successfully removed."
		}
		assert(result == success_status)

		# teardown
		self.details.save(statebefore)
		self.details.ensure_index("_id")