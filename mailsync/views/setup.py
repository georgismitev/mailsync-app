import datetime
import json
import tornado.escape
import logging

from tornado.web import authenticated

from mailsync import settings
from mailsync.forms import CreateDbDataForm
from mailsync.views.base import BaseView
from mailsync.libs.dates import unix_utc_now
from mailsync.models.sync import Sync
from mailsync.models.setup import setup_model
from mailsync.models.adapter import adapter
from mailsync.models.provider import Provider
from mailsync.models.database import Database

from formencode.validators import Invalid as InvalidForm

class DashboardView(BaseView):

    @authenticated
    def get(self):
        synced_lists = setup_model.get_synced_lists()

        self.render("dashboard.html", synced_lists=synced_lists)

class ListView(BaseView):
    
    @authenticated
    def post(self):
        try:
            api_details = json.loads(self.request.body)["api"]

            client_lists = Provider(api_details["provider"], api_details["key"]).get_lists()
            
            self.render_json({
                "status": "ok", 
                "data": client_lists
            })
        except Exception, err:
            logging.error(err)
            self.render_json({
                "status": "error",
                "data": "Something went wrong, please check again your API key."
            })

class ApiView(BaseView):

    @authenticated
    def get(self):
        self.render("setup/api.html")

    @authenticated
    def post(self):
        self.check_xsrf_cookie()

        provider = self.get_argument("api.provider")
        apikey = self.get_argument("api.key")

        list_id = self.get_argument("listid")
        list_name = self.get_argument("listname") 

        list_custom_fields = Provider(provider, apikey).get_select_fields(list_id)

        self.session["provider"] = { 
            "provider": provider,
            "apikey": apikey
        }

        self.session["list"] = { 
            "id": list_id,
            "name": list_name,
            "fields": list_custom_fields
        }

        self.redirect("/database")

class TableView(BaseView):

    @authenticated
    def post(self):
        try:
            self.check_xsrf_cookie()

            connection_details = json.loads(self.request.body)["connection_details"]
            tables = Database(connection_details).get_tables()
            
            self.render_json({
                "status": "ok",
                "data": tables
            })
        except Exception, err:
            logging.error(err)
            self.render_json({
                "status": "error",
                "data": "Something went wrong, please check your connection details."
            })
        
class DatabaseView(BaseView):

    @authenticated
    def get(self):
        errors = self.get_session_object("errors")
        driver = self.get_session_object("driver")

        self.render("setup/database.html", errors=errors, driver=driver)

    @authenticated
    def post(self):
        self.check_xsrf_cookie()

        try:
            driver = {
                "host": self.get_argument("driver.host", ""),
                "port" : self.get_argument("driver.port" , ""),
                "database": self.get_argument("driver.database" , ""),
                "username": self.get_argument("driver.username" , ""),
                "password": self.get_argument("driver.password" , ""),
                "driver": self.get_argument("driver.driver" , ""),
                "table": self.get_argument("tables" , "")
            }

            valid_form = CreateDbDataForm.to_python(driver)
        except InvalidForm, e:
            self.session["errors"] = e.unpack_errors()
            self.session["driver"] = driver
            self.redirect("/database")

        adapter.setup(driver)

        if adapter.is_valid_connection():
            self.session["driver"] = driver
            
            self.delete_session_object("errors")
            
            self.redirect("/columns")
        else:
            self.session["errors"] = {"invalid_connection": True}
            self.redirect("/database")

class ColumnView(BaseView):

    def _get_column_fields(self, fields):
        columns = []

        for field in fields:
            column = {}
            value = self.get_argument(field.key, None)
            
            if value:
                column["key"] = field.key
                column["value"] = value
                column["tag"] = field.tag
                
                columns.append(column)

        return columns

    def _decode(self, value):
        database_decode = settings.DATABASE["decode"]
        encoding = database_decode["encoding"]

        if database_decode["skip"]:
            value_decoded = value;
        elif database_decode["ignore"]:
            value_decoded = value.decode(encoding, "ignore")
        elif database_decode["replace"]:
            value_decoded = value.decode(encoding, "replace")
        else:
            value_decoded = value.decode(encoding)
        
        return value_decoded

    def _decode_rows(self, rows):
        rows_decoded = []
        
        for row in rows:
            columns_decoded = []
            for column in row:
                if isinstance(column, basestring) and not type(column) is unicode:
                    columns_decoded.append(self._decode(column))
                else:
                    columns_decoded.append(column)

            rows_decoded.append(columns_decoded)

        return rows_decoded

    @authenticated
    def get(self):
        provider = self.get_session_object("provider")
        list_data = self.get_session_object("list")
        driver = self.get_session_object("driver")

        if not provider or not list_data:
            self.redirect("/api")
        elif not driver:
            self.redirect("/database")
        else:
            table = driver["table"]
            database = Database(driver)
            
            header_row = database.get_columns(table)
            sample_rows = database.get_top_rows(table)

            rows = []
            [rows.append(sample_row) for sample_row in sample_rows]

            rows_decoded = self._decode_rows(rows)

            self.render("setup/column.html", select_fields=list_data["fields"],
                header_row=header_row, rows=rows_decoded)

    @authenticated
    def post(self):
        self.check_xsrf_cookie()

        provider = self.get_session_object("provider")
        list_data = self.get_session_object("list")
        driver = self.get_session_object("driver")
        
        if not provider or not list_data:
            self.redirect("/api")
        elif not driver:
            self.redirect("/database")
        
        lists = setup_model.check_synced_list(list_data["id"])

        if not lists:
            columns = self._get_column_fields(list_data["fields"])

            detail = {
                "database": dict(driver),
                "provider": dict(provider),
                "list": dict(list_data),
                "last_synced": unix_utc_now(),
                "date_created": unix_utc_now(),
                "columns": columns
            }
            
            detail_id = Sync().create(detail)

        self.delete_session_object("list")
        self.delete_session_object("driver")
        self.delete_session_object("provider")

        self.redirect("/dashboard")

class SyncView(BaseView):

    @authenticated
    def post(self):
        self.check_xsrf_cookie()

        id = json.loads(self.request.body)["idAttribute"]

        self.render_json(Sync().sync(id))

class SyncStatusView(BaseView):

    @authenticated
    def post(self):
        self.check_xsrf_cookie()
        
        id = json.loads(self.request.body)["idAttribute"]

        self.render_json(Sync().status_sync(id))

class SyncDeleteView(BaseView):
    
    @authenticated
    def delete(self, id):
        self.check_xsrf_cookie()
        
        self.render_json(Sync().delete_sync(id))