from datetime import datetime, time
import pytz
from mailsync.libs.dates import utc_unixtime_to_localtime
from mailsync import settings

# Converts unix time to readable date format 
# Used in the tooltips on the frontend
def dateformat(value, format="%d-%m-%Y-%H:%M"):
	try:
		_ = datetime.fromtimestamp(value, pytz.utc)
		return _.strftime(format)
	except:
		return None

# Localized unix timestamp
# def dateformat_local(value, format="%d-%m-%Y-%H:%M"):
def dateformat_local(value, format="%h %d'%Y at %H:%M"):
	value = utc_unixtime_to_localtime(value)

	return dateformat(value, format)

def base_url():
	if settings.PROXY is None:
		host = settings.WEB_APP["host"]
		port = settings.WEB_APP["port"]

		if port and int(port) > 0:
			base_url = "{0}:{1}".format(host, port)
		else:
			base_url = host

		return base_url
	else:
		return ""