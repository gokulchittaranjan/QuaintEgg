import web;

urls = (
	"/", "LoginPage",
	);

class LoginPage:
	def GET(self):
		
		render = web.template.render(WEBCONFIG["templateDir"], base='base')
		return render.LoginForm();

app = web.application(urls, locals())