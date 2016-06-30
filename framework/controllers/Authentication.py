# Controllers for managing authentication.

import web;

import json;
import hashlib;

from QuaintEgg.framework.controllers.ControllerUtil import *;

from QuaintEgg.lib.Util import GenericUtil;
from QuaintEgg.lib.DBDriver import RecordManager;
from QuaintEgg.framework.tables.Definition import AuthTable;

from Utils import Logging;

urls = (
		'/login', 'Login',
		'/logout', 'Logout',
		'/salt', 'Salt',
		'/user', 'User',
		'/signup', 'Signup',
);

logger = Logging.getLogger("Authentication");

# Setup default user for the database;
def setupDefaultDatabase(CONFIG):
	recordManager = RecordManager(WEBCONFIG, AuthTable);
	if len(recordManager.getRecords({"username":"root"}))==0:
		recordManager.addRecord({"username":"root", "md5key": hashlib.md5("root:root:auth").hexdigest(), "name": "Root", "meta":{},"role":["superadmin"]});
		logger.info("Default database created.");


class Signup:

	def PUT(self):

		jsonHook();

		logger = Logging.getLogger("ControllerUtil")
		logger.debug("Object Put");

		res = prepareResultObject();
		
		x = web.input(payload="");

		logger.debug("Put with %s" %(x.payload));
		try:
			payload = json.loads(x.payload);
			payload["role"] = ["user"];
			x.payload = json.dumps(payload);
		except:
			updateStatus(res, "failed");
			return json.dumps(res);

		recordManager = RecordManager(WEBCONFIG, AuthTable, web.ctx.ip);
		result = recordManager.addRecord(x.payload);
		
		if result:
			updateStatus(res, "done");
		else:
			updateStatus(res, "failed");
		return json.dumps(res);

class User(ClassicDBController):

	def __init__(self):
		ClassicDBController.__init__(self, WEBCONFIG, AuthTable);

class Salt:
	def GET(self):
		jsonHook();
		logger.debug("Salt requested.");

		res = prepareResultObject();
		
		newSalt = GenericUtil.getUniqueIdAsString();
		web.ctx.session.salt = newSalt;
		updateStatus(res, "done");
		res["response"]["salt"] = newSalt;
		return json.dumps(res);

class Logout:
	def GET(self):

		jsonHook();
		x = web.input(sessionkey="");
		res = prepareResultObject();
		if x["sessionkey"] in web.ctx.session.authkeys:
			updateStatus(res, "done");
			del web.ctx.session.authkeys[x["sessionkey"]];
		else:
			updateStatus(res, "failed");
		logger.debug("Logout.");
		return json.dumps(res);

class Login:
	def GET(self):

		jsonHook();
		logger.debug("Login.");
		x = web.input(payload="");
		
		res = prepareResultObject();
		salt = web.ctx.session.salt;
		found = False;
		roles = [];

		recordManager = RecordManager(WEBCONFIG, AuthTable, web.ctx.ip);
		objects = recordManager.getObjectForIndex(x.payload, allowProtected=True);
		currObject = recordManager.convertToRecord(x.payload);
		authkey = currObject["md5key"];
		for obj in objects:
			key = obj["md5key"];
			thiskey = hashlib.md5("%s:%s" %(salt, key)).hexdigest();
			print authkey, thiskey, obj
			if thiskey==authkey:
				found = True;
				roles = obj["role"];
				break;
		if found:
			updateStatus(res, "done");
			sessionKey = GenericUtil.getUniqueIdAsString();
			web.ctx.session.authkeys[sessionKey] = True;
			web.ctx.session.roles[sessionKey] = set(roles);
			#web.ctx.session.lastAccess[sessionKey] = 
			res["response"]["sessionkey"] = sessionKey;
			res["response"]["role"] = roles;
		return json.dumps(res);

app = web.application(urls, locals())

app.add_processor(authentication_processor);