import urlparse;
import urllib;
import json;

import requests;

class Proxy:

	def __init__(self, baseUrl):
		self.baseUrl = list(urlparse.urlparse(baseUrl));
		self.queryDict = dict(urlparse.parse_qsl(self.baseUrl[4]))
	
	def api(self, args):
		qd = dict(self.queryDict);
		qd.update(args);
		self.baseUrl[4] = urllib.urlencode(qd);
		return urlparse.urlunparse(self.baseUrl);

	def response(self, args, callType):
		try:
			fn = getattr(requests, callType)
			r = fn(self.api(args));
			if r.status_code!=200:
				return {"error": "200 not returned", "code": r.status_code, "text": r.text, "reason": r.reason};
			return json.dumps(r.json());
			#print urllib.urlopen(self.api(args)).read()
			#return json.loads(urllib.urlopen(self.api(args)).read());
		except IOError:
			return {"error": "Proxy address invalid."};
		except ValueError:
			return {"error": "Proxy did not return JSON"};
