from mailsync.api.campaignmonitor import CampaignMonitor
from mailsync.api.mailchimp import MailChimp
from mailsync.models.customfield import CustomField

class Provider(object):

	def __init__(self, provider, api_key):
		providers = {
			"mailchimp": MailChimp,
			"campaignmonitor": CampaignMonitor
		}

		self.provider = providers[provider](api_key)
		self.provider_name = provider

	def get_lists(self):
		return self.provider.get_lists()

	def get_select_fields(self, listid):
		select_fields = self.get_custom_fields(listid)

		if isinstance(self.provider, CampaignMonitor):
			select_fields.insert(0, CustomField("name-default", "Name (default)", "Name"))
			select_fields.insert(0, CustomField("email-default", "Email (default)", "EmailAddress"))
		elif isinstance(self.provider, MailChimp):
			for select_field in select_fields:
				if select_field.key == "email-address":
					select_field.key = "email-default"
					select_field.value = "Email (default)"
				elif select_field.key == "first-name":
					select_field.key = "first-name-default"
					select_field.value = "First Name (default)"
				elif select_field.key == "last-name":
					select_field.key = "last-name-default"
					select_field.value = "Last Name (default)"

		return select_fields

	def get_custom_fields(self, listid):
		return self.provider.get_list_custom_fields(listid)