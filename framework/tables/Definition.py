# Auth Table Definition
AuthTable = {
	
	"name": "auth",
	"description": {
		"username": "TEXT",
		"md5key": "TEXT",
		"name": "TEXT",
		"meta": "TEXT",
		"role": "TEXT",
	},
	"userFields": {
		"username": str, 
		"md5key": str,
		"name": str,
		"meta": dict,
		"role": list
	},
	"index": "username",
	"protectedFields": ["md5key"],
	"autogenerateIndex": False,
}