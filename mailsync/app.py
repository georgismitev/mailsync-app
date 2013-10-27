import os
import tornado.web

from os.path import join

# Views
from mailsync.views.auth import LoginView
from mailsync.views.setup import (
        DashboardView,
        ListView,
        ApiView,
        DatabaseView,
        TableView,
        ColumnView,
        SyncView,
        SyncStatusView,
        SyncDeleteView)

from mailsync.views.auth import LoginView, CreateUserView, LogoutView
from mailsync.paths import MEDIA_DIR
from mailsync import settings

settings = {
    "static_path": join(MEDIA_DIR, "static"),
    "media_path": MEDIA_DIR,
    "cookie_secret": "61oEETTzKXQAGaYdlkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "xsrf_cookies": True,
    "session": {
    	"duration": 3600, 
    	"regeneration_interval": 240, 
    	"domain": settings.WEB_APP['host']
	}
}

application = tornado.web.Application([
    # Auth
    (r"/login", LoginView),
    (r"/logout", LogoutView),
    (r"/create_user", CreateUserView),
    # Setup
    (r"^/$", DashboardView),
    (r"^/dashboard$", DashboardView),
    (r"^/api$", ApiView),
    (r"^/api/lists$", ListView),
    (r"^/database$", DatabaseView),
    (r"^/database/tables$", TableView),
    (r"^/columns$", ColumnView),
    (r"^/sync$", SyncView),
    (r"^/sync/status$", SyncStatusView),
    (r"^/sync/delete/(?P<id>\w+)$$", SyncDeleteView),
    # Static
	(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": settings['media_path']})
], **settings)