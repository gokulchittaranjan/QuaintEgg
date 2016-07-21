import web;
import argparse;

class QuaintEggApplication(web.application):
	def run(self, port=8080, host="0.0.0.0", *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, (host, port))

	@staticmethod
	def getParser():
		p = argparse.ArgumentParser();
		p.add_argument('-p', '--port', type=int, default=8080, help="Port to run on.");
		p.add_argument('-m', '--host', default="0.0.0.0", help="Host to run on.");
		p.add_argument('--reset-tmp', '-r', action="store_true", help="Reset the tmp directory.");
		p.add_argument('--reset-db', '-d', action="store_true", help="Reset the db.");
		return p;

	class SessionHook:
		def __init__(self, session):
			self.session = session;

		def session_hook(self):
			web.ctx.session = self.session;
			web.template.Template.globals['session'] = self.session;
