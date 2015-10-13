# -*- coding: utf-8 -*-
import pycouchdb
import logging

MAP_FUNCTION_COMMON = 'function(doc) {if(doc.%s=="%s"){emit(doc._id, doc);}}'
MAP_FUNCTION_MULTI_CONDITION = 'function(doc) {if(%s){emit(doc._id, doc);}}'
MESSAGE = {
	'ERROR_CONNECT': "ERROR: Can't connect to Database. Please check again",
	'EDIT_SUCCESS': "SUCCESS: Edited successfully!",
	'ADD_SUCCESS': "SUCCESS: Created successfully!",
	'DELETE_SUCCESS': "SUCCESS: Deleted successfully!",
	'ERROR_CATEGORY_FORM': "ERROR: Category name is empty"
}


class ConnectCouchdb(object):
	server = None
	database = None

	def __init__(self, server_name="http://admin:qwrtqwrt@116.118.119.102:5984", database_name="example"):
		try:
			self.server = pycouchdb.Server(server_name)
			self.get_database(database_name)
		except Exception, e:
			logging.error(str(e))
			raise

	def get_database(self, database_name):
		try:
			self.database = self.server.database(database_name)
		except Exception, e:
			logging.error(str(e))
			raise

	def save_doc(self, _doc):
		try:
			return self.database.save(_doc)
		except Exception, e:
			logging.error(str(e))
			raise

	def get_doc(self, _id):
		try:
			return self.database.get(_id)
		except Exception, e:
			logging.error(str(e))
			raise

	def delete_doc(self, _id):
		try:
			return self.database.delete(_id)
		except Exception, e:
			logging.error(str(e))
			raise

	def query_doc(self, _map_func=None):
		try:
			return list(self.database.temporary_query(_map_func))
		except Exception, e:
			logging.error(str(e))
			raise


