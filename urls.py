# URL--Controller Mappings

from QuaintEgg.framework.controllers import Authentication;
from QuaintEgg.framework.controllers import Pages;

urls = (
	'/framework/pages', Pages.app,
	'/framework/auth', Authentication.app,
);