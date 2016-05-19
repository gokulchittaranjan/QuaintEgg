# Web Server Configuration
import os;

curdir = os.path.dirname(__file__);

WEBCONFIG = {
	"dbName" : "master.db",
	"dbDriver": "sqlite",
	"tmpDir": "/tmp/AnnotationTool",
	"sessionDir": os.path.join(curdir, 'sessions'),
	"defaultSessionVariables": {},
	"templateDir": "framework/templates",
};