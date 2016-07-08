import web;
import json;

from QuaintEgg.lib.Util import GenericUtil;
from QuaintEgg.lib import DBDriver;
from QuaintEgg.lib.DBDriver import RecordManager;

from PythonUtils.Utils import Logging;

# Json hook
def jsonHook():
	web.header('Content-Type', 'application/json');

def prepareResultObject():
	res = {};
	res["status"] = False;
	res["statusText"] = "Request not processed.";
	return res;
	
def updateStatus(res, statusType):
	if statusType=="done":
		res["status"] = True;
		res["statusText"] = "Request processed.";
		res["response"] = {};
	elif statusType=="failed":
		res["statusText"] = "Request failed.";
	elif statusType=="permissionFail":
		res["statusText"] = "Username does not have the required permission."
	return res;

def openDBConnection(CONFIG):
	return DBDriver.getDBConnection(CONFIG["dbName"], CONFIG["dbDriver"]);

def validateRole(roles=set([])):
	path = web.ctx.homepath;
	
	if "/unauthenticated/" in path:
		return True;
	if type(roles)==list:
		roles = set(roles);
	x = web.input(sessionkey="");
	if not x.sessionkey in web.ctx.session.roles:
		print "sessionkey not found."
		return False;
	if len(web.ctx.session.roles[x.sessionkey].intersection(roles))>0 or "superadmin" in roles or "superadmin" in web.ctx.session.roles[x.sessionkey]:
		return True;
	else:
		return False;

# Authentication Processor.
def authentication_processor(handle):
	logger = Logging.getLogger("AuthenticationProcessor");
	path = web.ctx.path;
	x = web.input(sessionkey="");
	if (not x.sessionkey in web.ctx.session.authkeys or x.sessionkey=="") and not path in ["/login", "/salt", "/signup"] and not "/unauthenticated/" in path and not path in web.ctx.session.nonauthcalls:
		reply = dict();
		GenericUtil.addAuthenticationFailedInfo(reply);
		logger.warning("Unauthenticated API access; IP: %s" %(web.ctx.ip));
		jsonHook();
		return json.dumps(reply);
	else:
		logger.debug("Authentication succeded; IP: %s" %(web.ctx.ip));
		return handle();

class ClassicDBController:

	def __init__(self, CONFIG, tableObject):
		self.tableObject = tableObject;
		self.CONFIG = CONFIG;

	def PATCH(self):
		jsonHook();
		
		logger = Logging.getLogger("ControllerUtil")
		logger.debug("Object Update");

		
		res = prepareResultObject();
		if not validateRole():
			updateStatus(res, "permissionFail");
			return json.dumps(res);

		x = web.input(payload="");
		
		logger.debug("Update with %s" %(x.payload));

		recordManager = RecordManager(self.CONFIG, self.tableObject, web.ctx.ip);
		result = recordManager.updateRecord(x.payload);

		if result:
			updateStatus(res, "done");
		else:
			updateStatus(res, "failed");
		return json.dumps(res);

	def DELETE(self):

		jsonHook();

		logger = Logging.getLogger("ControllerUtil")
		logger.debug("Object Delete");

		res = prepareResultObject();
		if not validateRole():
			updateStatus(res, "permissionFail");
			return json.dumps(res);

		x = web.input(payload="");
		
		logger.debug("Delete with %s" %(x.payload));

		recordManager = RecordManager(self.CONFIG, self.tableObject, web.ctx.ip);
		result = recordManager.removeRecord(x.payload);

		if result:
			updateStatus(res, "done");
		else:
			updateStatus(res, "failed");
		return json.dumps(res);

	def PUT(self):

		jsonHook();

		logger = Logging.getLogger("ControllerUtil")
		logger.debug("Object Put");

		res = prepareResultObject();
		if not validateRole():
			updateStatus(res, "permissionFail");
			return json.dumps(res);
		
		x = web.input(payload="");

		logger.debug("Put with %s" %(x.payload));
		
		recordManager = RecordManager(self.CONFIG, self.tableObject, web.ctx.ip);
		result = recordManager.addRecord(x.payload);
		
		if result:
			updateStatus(res, "done");
		else:
			updateStatus(res, "failed");
		return json.dumps(res);

	def GET(self):
		
		jsonHook();

		logger = Logging.getLogger("ControllerUtil")
		logger.debug("Object Get");

		res = prepareResultObject();

		if not validateRole():
			updateStatus(res, "permissionFail");
			return json.dumps(res);

		
		x = web.input(payload="");

		logger.debug("Get with %s" %(x.payload));

		recordManager = RecordManager(self.CONFIG, self.tableObject, web.ctx.ip);
		objects = recordManager.getObjects(x.payload);
		if objects!=None:
			updateStatus(res, "done");
			res["response"] = dict();
			keys = [];
			for k,v in self.tableObject["userFields"].items():
				if v==str:
					keys.append([k, 'string']);
				else:
					keys.append([k, 'object']);
			res["response"]["keys"] = keys
			res["response"]["name"] = self.tableObject["name"];
			res["response"]["readonlyFields"] = self.tableObject["readonlyFields"];
			res["response"]["records"] = objects;
		else:
			updateStatus(res, "failed");

		return json.dumps(res);