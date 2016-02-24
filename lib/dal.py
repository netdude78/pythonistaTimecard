#!/usr/bin/python

import sqlite3
from util import synchronized

class Dal:
	"""
	Class to handle database abstraction for app
	"""

	_conn = None
	_db_schema = None

	def __init__(self, db_file='timecard.db'):
		"""
		Constructor.

		Optional db_file opens a connection to the specified file.
		
		Keyword Arguments:
			db_file {string} -- SQLite3 Database filename (default: {timecard.db})
		"""
		self._conn = sqlite3.connect(db_file)
		
		# populate schema info
		self._get_db_schema()

	def _get_db_schema(self):
		"""_get_db_schema()

		For internal use only.

		Fetches all tables from the sqlite_master table.  then executes pragma command
		to discover table columns.  Updates _db_schema as a dict keyed by table name and
		containing a list of column names.

		The resulting schema data will be used to sanity check field names and table names
		in database DAL calls.
		"""
		cur = self._conn.cursor()
		cur.row_factory = self._dict_factory
		rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

		if rows:
			tables = []
			for row in rows:
				tables.append(row['name'])

			self._db_schema = {}
			cur.row_factory = None
			for table in tables:
				cols = []
				for row in cur.execute("pragma table_info('%s')" %table).fetchall():
					cols.append(row[1])
				self._db_schema.update({table:cols})

	def _dict_factory(self, cursor, row):
		"""_dict_factory(cursor, row)

		For interal use only.
		
		factory method that will return a dictionary for each row returned from the sqlite db cursor.
		Dictionary keys will be string and correspond to the column name.
		
		Arguments:
			cursor {[type]} -- [cursor]
			row {[type]} -- [row]
		
		Returns:
			dict() -- {'column':value}
		"""
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def insert_record(self, table, *args, **kwargs):
		"""
		Insert a record to the database.  Return the record inserted to the caller if successful.
		
		Arguments:
			table name (required as first argument.  sqlite table name)

			*args
				tuple or list of values
				 *or*
				dictionary of column names and values 

			**kwargs
				To insert a record as a dictionary:
					insert_record('table', record=record_dict)

			This method will insert only the columns specified in the record dictionary

		Returns:
			Returns the inserted record.
		"""

		if table not in self._db_schema.keys():
			raise ValueError('Table name specified %s does not exist in DB.' %table)

		@synchronized
		def insert(table, values, cols=None):
			"""
			nested insert function

			inserts a row into the database.  Only callable inside of insert_record.
			Can be called from several places, depending on how insert_record is called.
			
			Arguments:
				table {[type]} -- [description]
				cols {[type]} -- [description]
				values {[type]} -- [description]
			
			Returns:
				[type] -- [description]
			
			Raises:
				ValueError -- [description]
			"""
			if cols:
				if len(cols) != len(values):
					raise ValueError("%s columns specified. %s values specified. Length must match" %(len(cols), len(values)))

				col_list = ""
				qs = ""
				for col in cols:
					col_list += "%s," %col
					qs += "?,"
				col_list = col_list.strip(',')
				qs = qs.strip(',')
				sql = "INSERT into %s (%s) VALUES (%s)" %(table, col_list, qs)
			else:
				qs = ""
				for val in values:
					qs += "?,"
				qs = qs.strip(',')
				sql = "INSERT INTO %s VALUES (%s)" %(table, qs)

			cur = self._conn.cursor()
			cur.row_factory = self._dict_factory

			cur.execute(sql, values)
			self._conn.commit()
			return cur.rowcount
			
		if 'record' in kwargs.keys():
			### a record has been passed with a keyword argument
			errors = []
			columns = []
			values = []
			for column in kwargs['record'].keys():
				if column not in self._db_schema[table]:
					errors.append("Column %s not in table %s" %(column, table))
				else:
					columns.append(column)
					values.append(kwargs['record'][column])
			if errors:
				raise ValueError(str(errors))

			return insert(table, values, columns)

		elif args and len(args) == 1 and (isinstance(args[0], list) or isinstance(args[0], tuple)):
			# a list of values only
			return insert(table, list(args[0]))
			
		elif args and len(args) == 1 and isinstance(args[0], dict):
			# a single dictionary of records supplied without keyword argument
			record = args[0]
			errors = []
			columns = []
			values = []
			for column in record.keys():
				if column not in self._db_schema[table]:
					errors.append("Column %s not in table %s" %(column, table))
				else:
					columns.append(column)
					values.append(record[column])
			if errors:
				raise ValueError(str(errors))

			return insert(table, values, columns)
			

	def get_record_by_id(self, table, *args, **kwargs):
		"""get_record_by_id(table, ...)
		
		Returns record by specified ID

		first arg after table should be the ID value.

		Optionally specify an array of field names like:
			get_record_by_id('test', 203, fields=['name', 'email'])
				will return the 'name' and 'email' columns from the test table
				where ID = 203
		
		Arguments:
			table {[string]} -- [description]
			*args {[ID]} -- [add ID value]
			**kwargs {[type]} -- [fields - optional]
		
		Returns:
			[type] -- [description]
		
		Raises:
			ValueError -- [description]
		"""
		if table not in self._db_schema.keys():
			raise ValueError('Table name specified %s does not exist in DB.' %table)
		cur = self._conn.cursor()
		cur.row_factory = self._dict_factory

		if not kwargs and len(args) == 1:
			# should mean the id field is 'id' (default)
			# and single argument after table is the ID

			sql = "SELECT * from %s WHERE id=?" %table
			print sql
			return cur.execute(sql, str(args[0])).fetchall()
		if kwargs:
			x_args = dict(kwargs)
			if 'fields' in x_args:
				f_list = ""
				for field in x_args.pop('fields'):
					f_list += "%s ," %field
				f_list = f_list.strip(',')

				sql = "SELECT %s from %s " %(f_list, table)
			print sql
			return cur.execute(sql).fetchall()

	def search_for_records(self, table, *args, **kwargs):
		if table not in self._db_schema.keys():
			raise ValueError('Table name specified %s does not exist in DB.' %table)
		cur = self._conn.cursor()
		cur.row_factory = self._dict_factory

		if kwargs:
			x_args = dict(kwargs)
			if 'fields' in x_args:
				f_list = ""
				for field in x_args.pop('fields'):
					f_list += "%s ," %field
				f_list = f_list.strip(',')
				sql = "SELECT %s from %s " %(f_list, table)
			else:
				sql = "SELECT * from %s " %table

			num_criteria = len(x_args['criteria'])
			x = 0
			sql += "WHERE "
			criterium = []
			print 'x_args: %s' %x_args
			for (field,op,criteria) in x_args['criteria']:
				sql += "%s %s ? " % (str(field), str(op))
				criterium.append(str(criteria))
				x += 1
				if x < num_criteria:
					sql += "AND "

			print sql
			return cur.execute(sql, tuple(criterium)).fetchall()

	def update_record(self, table, *args, **kwargs):
		if table not in self._db_schema.keys():
			raise ValueError('Table name specified %s does not exist in DB.' %table)

		pass

	def delete_record(self, table, *args, **kwargs):
		if table not in self._db_schema.keys():
			raise ValueError('Table name specified %s does not exist in DB.' %table)


		pass


	@synchronized
	def create_table(self, table, fields):
		"""create_table(table, fields)
		
		Fields should be a dictionary:
			key: column name
			value: column type and options
		
		Arguments:
			table {[string]} -- [table name]
			fields {[list of dictionaries]} -- [array of dictionaries:]
				column_name
				type
				options (optional)
		
		Raises:
			ValueError -- [description]

		NOTE: This method should never be called from any web-facing code.  It is potentially
		unsafe and care should be taken to avoid SQL injection.
		"""
		if table in self._db_schema.keys():
			raise ValueError('Table name specified %s is already in DB.' %table)

		sql = 'CREATE TABLE %s (' %table
		num_fields = len(fields)
		i = 0
		for field in fields:
			sql += "%s %s" %(field['column_name'], field['type'])
			if 'options' in field:
				sql += " %s" %field['options']
			i += 1
			if i < num_fields:
				sql += ','
		sql += ')'

		cur = self._conn.cursor()
		cur.execute(sql)
		self._conn.commit()
		self._get_db_schema()


	@synchronized
	def drop_table(self, table):
		"""
		drop_table(table)
		
		drops table specified
		
		Arguments:
			table {[string]} -- [table name to drop]

		NOTE:  This method should never be called from any web-facing code.  It is potentially
		unsafe and care should be taken to avoid SQL injection.
		"""

		cur = self._conn.cursor()
		cur.execute("DROP TABLE %s" %table)
		self._conn.commit()
		self._get_db_schema()







