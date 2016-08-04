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

	def map(self, headers):
		if "set-cookie" in headers:
			cookies = map(lambda x: x.strip(), headers['set-cookie'].split(";"));
			for ii in xrange(0, len(cookies)):
				cookie = cookies[ii];
				if cookie.split("=")[0]=="webpy_session_id":
					cookies[ii] = "proxy_webpy_session_id=%s" %("=".join(cookie.split("=")[1:]));
				if cookie.split("=")[0]=="proxy_webpy_session_id":
					cookies[ii] = "backward_webpy_session_id=%s" %("=".join(cookie.split("=")[1:]));
			headers['set-cookie'] = ";".join(cookies);

	def invmap(self, headers):
		newHeaders = {};
		for k,v in headers.items():
			if k[0:5]!="HTTP_":
				continue;
			if k!="HTTP_COOKIE":
				newHeaders[k[5:]] = v;
				continue;
			cookies = map(lambda x: x.strip(), v.split(";"));
			for ii in xrange(0, len(cookies)):
				cookie = cookies[ii];
				if cookie.split("=")[0]=="proxy_webpy_session_id":
					cookies[ii] = "webpy_session_id=%s" %("=".join(cookie.split("=")[1:]));
				if cookie.split("=")[0]=="webpy_session_id":
					cookies[ii] = "forward_webpy_session_id=%s" %("=".join(cookie.split("=")[1:]));
			newHeaders['COOKIE'] = ";".join(cookies);
		return newHeaders;

	def response(self, args, callType, env = {}):
		try:
			fn = getattr(requests, callType)
			env = self.invmap(env);
			print "env", env
			r = fn(self.api(args), headers=env);
			if r.status_code!=200:
				return {"error": "200 not returned", "code": r.status_code, "text": r.text, "reason": r.reason}, {};
			headers = r.headers;
			self.map(headers);
			#print headers
			return json.dumps(r.json()), headers;
			#print urllib.urlopen(self.api(args)).read()
			#return json.loads(urllib.urlopen(self.api(args)).read());
		except IOError:
			return {"error": "Proxy address invalid."}, {'content-type':'application/json'};
		#except ValueError:
		#	return {"error": "Proxy did not return JSON"}, {'content-type':'application/json'};
