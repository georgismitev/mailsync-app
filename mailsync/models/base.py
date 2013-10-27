class BaseModel(object):
    
    page_size = 50

    def paginate(self, cursor, page=None):
        
        page = 1 if page == None else int(page)
        page = 1 if page == 0 else page
        
        rows = cursor.clone().count()
        total_pages = rows/self.page_size
        total_pages = 1 if total_pages == 0 else total_pages
        
        page = total_pages if page > total_pages else page

        skip = self.page_size * (page - 1)

        result = cursor.limit(self.page_size).skip(skip)

        pagination = {
                "pages": total_pages, 
                "current_page": page,
                "result": result 
        }
        
        return pagination

    def get_driver(self, database_data):
        return {
            "host": database_data.host,
            "port" : database_data.port,
            "database": database_data.database,
            "username": database_data.username,
            "password": database_data.password,
            "driver": database_data.driver,
            "table": database_data.table
        }

    def get_columns(self, columns_data):
        columns_dict = {} 
        
        for column_data in columns_data:
            columns_dict[column_data.tag] = column_data.value

        return columns_dict

    def get_last_inserted_id(self, list_data, table, primary_key):
        # nothing synced for this list
        if not (list_data.last_inserted_id and list_data.status and list_data.inserted_rows and list_data.rows_to_be_inserted):
            last_inserted_id = 0
        elif list_data.last_inserted_id:
            last_inserted_id = list_data.last_inserted_id
        else:
            last_inserted_id = adapter.get_last_inserted_id(table, primary_key, "first")

        return last_inserted_id