import json;
import uuid;
from PythonUtils.SqliteDBConnection import DBConnection;
from QuaintEgg.lib.Util import GenericUtil;

from PythonUtils.Utils import Logging;

class DBDriver:

	@staticmethod
	def getDBConnection(dbName, dbType):
		if dbType=='sqlite':
			return DBConnection(dbName);

class RecordsAndObjects:

	@staticmethod
	def validateObject(obj, mandatoryFields, index, autogenerateIndex=False):
		logger = Logging.getLogger("RecordsAndObjects.validateObject");

		if type(obj)==str or type(obj)==unicode:
			logger.debug("Validing object %s" %(obj))
			try:
				obj = json.loads(obj);
			except ValueError:
				logger.error("Object %s could not be converted to json" %(obj))
				return None;
		if type(obj)!=dict:
			return None;
		for m,tp in mandatoryFields.items():
			if not m in obj:
				obj[m] = tp();
				logger.warning("created field %s in object %s" %(m, json.dumps(obj)))
			if not ( (type(obj[m])==unicode and tp==str) or (type(obj[m])==str and tp==unicode) or (type(obj[m])==tp) ):
				if obj[m]==None:
					obj[m] = tp();
				else:
					logger.error("field %s in invalid type in object %s" %(m, json.dumps(obj)));
					logger.error("type is %s" %(type(obj[m])))
					return None;
		
		if not index in obj or (type(obj[index])!=str and type(obj[index])!=unicode) or obj[index]=="":
			if not autogenerateIndex:
				logger.error("index %s does not exist in object %s" %(index, json.dumps(obj)))
				return None;
			else:
				obj[index] = GenericUtil.getUniqueIdAsString();
		return obj;

	@staticmethod
	def convertObjectToRecord(obj, mandatoryFields, index, autogenerateIndex=False):
		obj = RecordsAndObjects.validateObject(obj, mandatoryFields, index, autogenerateIndex);
		if obj==None:
			return None;
		newObj = {};
		for m, tp in mandatoryFields.items():
			if tp==str:
				newObj[m] = obj[m];
			else:
				newObj[m] = json.dumps(obj[m]);
		if not index in newObj:
			newObj[index] = str(uuid.uuid4());
		return newObj;

	@staticmethod
	def convertRecordToObject(record, mandatoryFields):
		obj = dict.fromkeys(mandatoryFields.keys());
		for m, tp in mandatoryFields.items():
			if not m in record:
				continue;
			if tp==str:
				obj[m] = record[m];
			else:
				try:
					obj[m] = json.loads(record[m]);
				except ValueError:
					continue;
		return obj;

	@staticmethod
	def updateRecord(original, new):
		for k,v in new.items():
			if k in original:
				original[k] = new[k];

class RecordManager:
	def __init__(self, CONFIG, tableObject, IP="127.0.0.1"):
		self.CONFIG = CONFIG;
		self.tableObject = tableObject;
		self.openConnectionForTable();
		self.IP = IP;

	def openConnectionForTable(self):
		self.connection = DBDriver.getDBConnection(self.CONFIG["dbName"], self.CONFIG["dbDriver"]);
		if not "IP" in self.tableObject["description"]:
			self.tableObject["description"]["IP"] = "TEXT";
		if not "timestamp" in self.tableObject["description"]:
			self.tableObject["description"]["timestamp"] = "TEXT";
		self.connection.createTable(self.tableObject["name"], self.tableObject["description"]);
	
	def convertToRecord(self, record):
		return self.__preprocessRecord(record);

	def __preprocessRecord(self, record):
		return RecordsAndObjects.convertObjectToRecord(record, self.tableObject["userFields"], self.tableObject["index"], self.tableObject["autogenerateIndex"]);

	def __removeProtected(self, records):
		for ii in xrange(0, len(records)):
			for f in self.tableObject["protectedFields"]:
				if f in records[ii]:
					records[ii][f] = "hidden.";

	def getObjects(self, record, allowProtected=False):
		if type(record)==str or type(record)==unicode:
			try:
				record =json.loads(record);
			except ValueError:
				return [];
		records = self.connection.getRecords(self.tableObject["name"], record);
		records = map(lambda x: RecordsAndObjects.convertRecordToObject(x, self.tableObject["userFields"]), records);
		if not allowProtected:
			self.__removeProtected(records);
		return records;

	def getRecords(self, record = {}, allowProtected=False):
		if type(record)==str or type(record)==unicode:
			try:
				record =json.loads(record);
			except ValueError:
				return [];
		records = self.connection.getRecords(self.tableObject["name"], record);
		if not allowProtected:
			self.__removeProtected(records);
		return records;

	def getRecordForIndex(self, record, allowProtected=False):
		record = self.__preprocessRecord(record);
		if record == None or not self.tableObject["index"] in record:
			return [];
		fetchFilter = {self.tableObject["index"]: record[self.tableObject["index"]]};
		records = self.connection.getRecords(self.tableObject["name"], fetchFilter);
		if not allowProtected:
			self.__removeProtected(records);
		return records;

	def getObjectForIndex(self, record, allowProtected=False):
		records = self.getRecordForIndex(record, allowProtected);
		records = map(lambda x: RecordsAndObjects.convertRecordToObject(x, self.tableObject["userFields"]), records);
		return records;

	def removeRecord(self, record):
		record = self.__preprocessRecord(record);
		if record==None:
			return False;
		fetchFilter = {self.tableObject["index"]: record[self.tableObject["index"]]};
		self.connection.deleteRecord(self.tableObject["name"], fetchFilter);
		return True;

	def addRecord(self, record):
		record = self.__preprocessRecord(record);
		if record==None:
			return False;
		existingRecord = self.getRecordForIndex(record);
		if len(existingRecord)>0:
			return False;
		record["IP"] = self.IP;
		record["timestamp"] = GenericUtil.getTimeStampAsString();
		self.connection.addRecord(self.tableObject["name"], record);
		return True;

	def updateRecord(self, record):
		record = self.__preprocessRecord(record);
		if record==None:
			return False;
		oldRecord = self.getRecordForIndex(record);
		if len(oldRecord)!=1:
			return False;
		oldRecord = oldRecord[0];
		RecordsAndObjects.updateRecord(oldRecord, record);
		result1 = self.removeRecord(oldRecord);
		result2 = self.addRecord(oldRecord);
		return result1 and result2;