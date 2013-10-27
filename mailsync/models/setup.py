import logging

from mailsync.models.base import BaseModel
from mailsync.models.adapter import adapter
from mailsync.models.sqlite import details_table, columns_table, database_table, provider_table, lists_table

class SetupModel(BaseModel):
    
    def __init__(self):
        super(SetupModel, self).__init__()

    def _get_provider(self, provider_name):
        providers = {
            "mailchimp": "MailChimp",
            "campaignmonitor": "Campaign Monitor"
        }

        return providers[provider_name]

    def _get_last_inserted_id(self, list_data, table, primary_key):
        # nothing synced for this list
        if not (list_data.last_inserted_id and list_data.status and list_data.inserted_rows and list_data.rows_to_be_inserted):
            last_inserted_id = 0
        elif list_data.last_inserted_id:
            last_inserted_id = list_data.last_inserted_id
        else:
            last_inserted_id = adapter.get_last_inserted_id(table, primary_key, "first")

        return last_inserted_id

    def get_synced_lists(self):
        synced_lists = []
        
        for synced_list_data in details_table.get_details():
            details_id = synced_list_data._id

            database_data = database_table.find_detail(details_id)
            provider_data = provider_table.find_detail(details_id)
            list_data = lists_table.find_detail(details_id)
            columns_data = columns_table.find_details(details_id)

            if database_data and provider_data and list_data and columns_data:

                driver = self.get_driver(database_data)
                adapter.setup(driver)

                table = database_data.table
                primary_key = adapter.get_primary_key(table)

                last_inserted_id = self._get_last_inserted_id(list_data, table, primary_key)
                columns_dict = self.get_columns(columns_data)

                try:
                    rows_to_be_synced = adapter.get_rows_to_be_inserted(table, columns_dict, primary_key, last_inserted_id)
                    
                    provider_name = self._get_provider(provider_data.provider) 
                    
                    synced_lists.append({
                        "id": synced_list_data._id,
                        "name": list_data.name,
                        "last_synced": synced_list_data.last_synced,
                        "provider": provider_name,
                        "database": database_data,
                        "table": table,
                        "rows_to_be_synced": len(rows_to_be_synced)
                    })
                except Exception, err:
                    logging.error(err)
                    continue

        return synced_lists

    def check_synced_list(self, list_provider_id):
        return lists_table.find_list_by_listid(list_provider_id)

setup_model = SetupModel()