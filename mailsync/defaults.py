import sys

try:
    import json
except ImportError:
    import simplejson as json

try:
    config_file = file("/etc/mailsync.conf").read()
    config = json.loads(config_file)
except Exception, err:
    print "There was an error in your configuration file (/etc/mailsync.conf)"
    raise err

_web_app = config.get("web_app", {})
host = _web_app.get("host", "http://127.0.0.1")

if not host.startswith("http"):
    host = "http://{0}".format(host)

WEB_APP = {
    "host": host,
    "port": _web_app.get("port", 4321)
}

PROXY = config.get("proxy", None) # Relative baseurl if True

SQLITE_PATH = config.get("sqlite_path", "/usr/local/mailsync/mailsync.db")
LOGFILE_PATH = config.get("logfile_path", "/usr/local/mailsync/mailsync.log")

TIMEZONE = config.get("timezone","UTC")

ROWS = config.get("rows", 3)

# validate database settings
def str_to_bool(val):
	if val == "true": 
		return True
	else: #val == "false":
		return False

_database = config.get("database", {
	"decode": {
		"skip": True,
		"ignore": False,
		"replace": False,
		"encoding": "utf-8"
	},
	"encode": {
		"skip": True,
		"encoding": "utf-8"
	}
})

_database_decode = _database.get("decode", { 
	"decode": {
		"skip": True,
		"ignore": False,
		"replace": False,
		"encoding": "utf-8"
	}
})

_database_decode_skip = _database_decode.get("skip", False)
if not _database_decode_skip in ("true", "false"):
	_database_decode_skip = True
else:
	_database_decode_skip = (str_to_bool(_database_decode_skip))

_database_decode_ignore = _database_decode.get("ignore", False)
if not _database_decode_ignore in ("true", "false"):
	_database_decode_ignore = False
else:
	_database_decode_ignore = (str_to_bool(_database_decode_ignore))

_database_decode_replace = _database_decode.get("replace", False)
if not _database_decode_replace in ("true", "false"):
	_database_decode_replace = False
else:
	_database_decode_replace = (str_to_bool(_database_decode_replace))

_database_encode = _database.get("encode", {
	"skip": True,
	"encoding": "utf-8"
})

_database_encode_skip = _database_encode.get("skip", False)
if not _database_encode_skip in ("true", "false"):
	_database_encode_skip = True
else:
	_database_encode_skip = (str_to_bool(_database_encode_skip))

DATABASE = {
	"decode": {
		"skip": _database_decode_skip,
		"ignore": _database_decode_ignore,
		"replace": _database_decode_replace,
		"encoding": _database_decode.get("encoding")
	},
	"encode": {
		"skip": _database_encode_skip,
		"encoding": _database_encode.get("encoding")
	}
}