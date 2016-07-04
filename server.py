#!/usr/bin/python

import web;
import os;
import optparse;
import sys;
import shutil;
#from collections import defaultdict;
from config import *;
from urls import *;

from QuaintEgg.lib.Util import GenericUtil;

web.config.debug = False

app = web.application(urls, globals())

#sessionDict = {'authkeys': dict(), 'salt': '', 'roles': defaultdict(list), 'nonauthcalls': []};
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

def session_hook():
	web.ctx.session = session;
	web.template.Template.globals['session'] = session;

application = None;

if __name__ == "__main__":
	p = optparse.OptionParser();
	p.add_option('--reset-tmp', '-r', action="store_true", help="reset the tmp directory.");
	p.add_option('--reset-db', '-d', action="store_true", help="reset the db.");
	options, arguments = p.parse_args();
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
	sys.argv = arguments;
	app.add_processor(web.loadhook(session_hook))
	app.run();
else:
	if not os.path.exists(WEBCONFIG["tmpDir"]):
		os.mkdir(WEBCONFIG["tmpDir"]);
	application = app.wsgifunc();