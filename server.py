#!/usr/bin/python

import web;
import os;
import sys;
import shutil;
#from collections import defaultdict;
from config import *;
from urls import *;

from QuaintEgg.lib.Util import GenericUtil;
from QuaintEgg.lib.WebPyCustomizations  import QuaintEggApplication;

web.config.debug = False

app = QuaintEggApplication(urls, globals());

sessionDict = GenericUtil.getDefaultSessionDict();
for k,v in WEBCONFIG["defaultSessionVariables"].items():
	sessionDict[k] = v;

session = web.session.Session(app, web.session.DiskStore(WEBCONFIG["sessionDir"]), initializer=sessionDict)

WEBCONFIG["session"] = session;
WEBCONFIG["curdir"] = curdir;
WEBCONFIG["defaultSessionVariables"] = sessionDict;

import __builtin__;
__builtin__.curdir = curdir;
__builtin__.WEBCONFIG = WEBCONFIG;


application = None;

if __name__ == "__main__":
	p = QuaintEggApplication.getParser()
	options = p.parse_args();
	if options.reset_tmp:
		print "Resetting tmp directory...";
		if os.path.exists(WEBCONFIG["tmpDir"]):
			shutil.rmtree(WEBCONFIG["tmpDir"]);
	if options.reset_db:
		print "Resetting the database...";
		if os.path.exists(WEBCONFIG["dbName"]):
			os.remove(WEBCONFIG["dbName"]);
		Authentication.setupDefaultDatabase(WEBCONFIG);
	if not os.path.exists(WEBCONFIG["tmpDir"]):
		os.mkdir(WEBCONFIG["tmpDir"]);
	sessionHook = QuaintEggApplication.SessionHook(session);
	app.add_processor(web.loadhook(sessionHook.session_hook))
	app.run(port=options.port, host=options.host);
else:
	if not os.path.exists(WEBCONFIG["tmpDir"]):
		os.mkdir(WEBCONFIG["tmpDir"]);
	application = app.wsgifunc();