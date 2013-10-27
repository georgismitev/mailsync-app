import formencode
from formencode import validators
from mailsync.models.auth import user_model

class Driver(formencode.FancyValidator):
	def _to_python(self, value, state):
		if value in ["mysql", "postgresql"]:
			return value

class CreateDbDataForm(formencode.Schema):
	driver = formencode.All(Driver())
	username = formencode.All(validators.String(not_empty=True, min=1))
	password = formencode.All(validators.String(not_empty=True, min=1))
	host = formencode.All(validators.String(not_empty=True, min=1))
	database = formencode.All(validators.String(not_empty=True, min=1))
	port = formencode.All(validators.Int(not_empty=True, min=1024))
	table = formencode.All(validators.String(not_empty=True, min=1))

class UniqueUsername(formencode.FancyValidator):

    def _to_python(self, value, state):
        user = user_model.username_exists(value)
        if user == 1:
            raise formencode.Invalid('The username already exists', value, state)

        return value

class CreateUserForm(formencode.Schema):
    username = formencode.All(validators.String(not_empty=True, min=4),UniqueUsername())
    password = validators.String(not_empty=True, min=4)