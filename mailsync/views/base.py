import tornado.web
from jinja2 import Environment, FileSystemLoader

from mailsync import settings
from mailsync import __version__
from mailsync.paths import TEMPLATES_DIR
from mailsync.template import dateformat, dateformat_local, base_url
from mailsync.libs.session import SqliteSession

class BaseView(tornado.web.RequestHandler):

	def initialize(self):
		self.session = self._create_session()
		
		# Template variables. Passing that dictionary to Jinja
		self.template_vars = {
			"url": self.request.uri,
			"version": __version__,
			"xsrf": self.xsrf_form_html(),
			"session": self.session,
			"base_url": base_url()
		}

		super(BaseView, self).initialize()

	def get_current_user(self):
		try:
			return self.session["user"]
		except KeyError:
			return None

	def write_error(self, status_code, **kwargs):
		error_trace = None

		if "exc_info" in kwargs:
			import traceback
			
		error_trace= ""
		for line in traceback.format_exception(*kwargs["exc_info"]):
			error_trace += line 

		self.render("error.html", 
			status_code=status_code,
			error_trace=error_trace,
			)

	# def _render_template_encode

	def render(self, template, *args, **kwargs):
		env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
		env.filters["date"] = dateformat
		env.filters["date_local"] = dateformat_local

		kwargs["app"] = self.template_vars # application wide constants and variables

		try:
			template = env.get_template(template)
		except:
			pass

		rendered_template = template.render(*args, **kwargs)
		
		if not settings.DATABASE["encode"]["skip"]:
			rendered_template = rendered_template.encode(settings.DATABASE["encode"]["encoding"])

		self.write(rendered_template)

	def _create_session(self):
		session_id = self.get_secure_cookie("mailsyncapp_session_id")
		
		kw = {	
			"security_model": [],
			"duration": self.settings["session"]["duration"],
			"ip_address": self.request.remote_ip,
			"user_agent": self.request.headers.get("User-Agent"),
			"regeneration_interval": self.settings["session"]["regeneration_interval"]
		}

		new_session = None
		old_session = None

		old_session = SqliteSession.load(session_id)

		if old_session is None or old_session._is_expired(): # create new session
			new_session = SqliteSession(**kw)

		if old_session is not None:
			if old_session._should_regenerate():
				old_session.refresh(new_session_id=True)
			return old_session

		return new_session

	def finish(self, chunk = None):
		if self.session is not None and self.session._delete_cookie:
			self.clear_cookie("mailsyncapp_session_id")
		elif self.session is not None:
			self.session.refresh() # advance expiry time and save session
			self.set_secure_cookie("mailsyncapp_session_id", self.session.session_id, 
				expires_days=None,
				expires=self.session.expires,)

		super(BaseView, self).finish(chunk = chunk)

	def get_session_object(self, key):
		try:
			return self.session[key]
		except:
			return None

	def delete_session_object(self, key):
		try:
			del self.session[key]
		except:
			pass

	def render_json(self, data):
		self.set_header("Content-Type", "application/json")
		self.write(tornado.escape.json_encode(data))