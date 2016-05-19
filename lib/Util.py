import uuid;
import json;
import datetime;

class GenericUtil:

	@staticmethod
	def getTimeStampAsString():
		return "%s" %(datetime.datetime.now())

	@staticmethod
	def getUniqueIdAsString():
		return str(uuid.uuid4())

	@staticmethod
	def addAuthenticationFailedInfo(dct):
		dct["status"] = False;
		dct["message"] = "Authentication failed.";
