"""
An implementation of the Database API v2.0 interface to DAL VOTable responses.
This only supports read-only access.  
"""
from .query import Iter

apilevel = "2.0"
threadsafety = 2
paramstyle = "n/a"

__all__ = "STRING BINARY NUMBER DATETIME ROWID".split()

class Error(StandardError):
    """
    DB-API base exception
    """
    pass
class Warning(StandardError):
    """
    DB-API warnging
    """
    pass
class InterfaceError(Error):
    """
    DB-API exception indicating an error related to the database interface 
    rather than the database itself.
    """
    pass
class DatabaseError(Error):
    """
    DB-API exception indicating an error related to the database.
    """
    pass
class DataError(DatabaseError):
    """
    DB-API exception indicating an error while processing data (e.g. divide
    by zero, numeric value out-of-range, etc.)
    """
    pass
class OperationalError(DatabaseError):
    """
    DB-API exception indicating an error related to the database's operation 
    and not necessarily under the control of the programmer.
    """
    pass
class IntegrityError(DatabaseError):
    """
    DB-API exception indicating an inconsistancy in the database integrity.
    """
    pass
class InternalError(DatabaseError):
    """
    DB-API exception indicating an internal error that might indicate that 
    a connection or cursor is no longer valid.
    """
    pass
class ProgrammingError(DatabaseError):
    """
    DB-API exception indicating an erroneous request (e.g. column not found)
    """
    pass
class NotSupportedError(DatabaseError):
    """
    DB-API exception indicating a request is not supported
    """
    pass


class TypeObject(object):
    def __init__(self,*values):
        self._values = values

    @property
    def id(self): return self._values[0]

    def __eq__(self, other):
        if not isinstance(other, TypeObject): 
            return False
        if other.id in self._values:
            return True
        return self.id in other._values

    def __ne__(self, other):
        return not self.__eq__(other)

STRING = TypeObject(0)
BINARY = TypeObject(1)
NUMBER = TypeObject(2)
DATETIME = TypeObject(3, STRING.id)
ROWID = TypeObject(4, NUMBER.id)

def connect(source):
    raise NotSupportedError("Connection objects not supported")

class Cursor(Iter):
    """
    A class used to walk through a query response table row by row, 
    accessing the contents of each record (row) of the table.  This class
    implements the Python Database API.
    """

    def __init__(self, results):
	"""Create a cursor instance.  The constructor is not typically called 
        by directly applications; rather an instance is obtained from calling a 
        DalQuery's execute().
	"""
        Iter.__init__(self, results)
	self._description = self._mkdesc()
	self._rowcount = self.resultset.size
	self._arraysize = 1

    def _mkdesc(self):
        flds = self.resultset.fieldnames()
        out = []
        for name in flds:
            fld = self.resultset.getdesc(name)
            typ = STRING
            if fld.datatype in \
       "short int long float double floatComplex doubleComplex boolean".split():
                typ = NUMBER
            elif fld.datatype in "char unicodeChar unsignedByte".split():
                typ = STRING
                
            out.append( (name, typ) )

        return tuple(out)

    @property
    def description(self):
        """
        a read-only sequence of 2-item seqences.  Each seqence describes 
        a column in the results, giving its name and type_code.
        """
        return self._description 

    @property
    def rowcont(self):
        """
        the number of rows in the result (read-only)
        """
        return self._rowcount

    @property
    def arraysize(self):
        """
        the number of rows that will be returned by returned by a call to 
        fetchmany().  This defaults to 1, but can be changed.  
        """
        return self._arraysize
    @arraysize.setter
    def arraysize(self, value):
        if not value: value = 1
        self._arraysize = value

    def infos(self):
	"""Return any INFO elements in the VOTable as a dictionary.

	:Returns:
	    A dictionary with each element corresponding to a single INFO,
	    representing the INFO as a name:value pair.
	"""
	pass

    def fetchone(self):
	"""Return the next row of the query response table.

	:Returns:
	    The response is a tuple wherein each element is the value of the
	    corresponding table field.  
	"""
        try:
            rec = next()
            out = []
            for name in self.resultset.fieldnames():
                out.append(rec[name])
            return out
        except StopIteration:
            return None
	

    def fetchmany(self, size=None):
	"""Fetch the next block of rows from the query result.

	:Args:
	    *size*: The number of rows to return (default: cursor.arraysize).

	:Returns:
	    A list of tuples, one per row.  An empty sequence is returned when
	    no more rows are available.  If a DictCursor is used then the output
	    consists of a list of dictionaries, one per row.
	"""
	if not size: size = self.arraysize
        out = []
        for i in xrange(size):
            out.append(self.fetchone())

    def fetchall(self):
	"""Fetch all remaining rows from the result set.

	:Returns:
	    A list of tuples, one per row.  An empty sequence is returned when
	    no more rows are available.  If a DictCursor is used then the output
	    consists of a list of dictionaries, one per row.
	"""
	pass

    def nextset(self):
	"""Advance to the next result set.

	Advance to the next result set in a multi result-set query response.
	Any remaining data in the current result set is skipped.
	"""
	raise NotSupportedError("nextset")

    def scroll(self, value, mode=None):
	"""Move the row cursor.

	:Args:
	    *value*: The number of rows to skip or the row number to position to.

	    *mode*: Either "relative" for a relative skip, or "absolute" to position to a row by its absolute index within the result set (zero indexed).
	"""
	if mode == "absolute":
            self.pos = value
        else:
            self.pos += value

    def getbyid(self, key):
        """
        return the value of the column with the given ID value
        """
        pass

    def getbyname(self, key):
        """
        return the value of the first column with the given name
        """
        pass

    def getbyucd(self, key):
        """
        return the value of the first column with the given UCD
        """
        pass

    def getbyutype(self, key):
        """
        return the value of the first column with the given UType
        """
        pass

    def getdataurl(self):
        """
        return the URL contained in the access URL column which can be used 
        to retrieve the dataset described by this record.  None is returned
        if no such column exists.
        """
        pass

    def getdataset(self):
	"""
        Get the dataset described by this record

	:Returns:
	    An file-like object which may be read to retrieve the referenced 
            dataset.
	"""
	pass

    def cachedataset(self, filename=None):
        """
        retrieve the dataset described by this record and write it out to 
        a file with the given name.  If the file already exists, it will be
        over-written.

        :Args:  
            *filename*:   the path to a file to write to.  If None, a default
                            name is attempted based on the record title and 
                            format
        """
        pass

    def makefilename(self):
        """
        create a reasonable default name for the dataset described by this 
        record based on data in the record.  It is not guaranteed to be unique.  
        """
        # abstract; specialized for the different service types
        pass

    def close():
	"""Close the cursor object and free all resources.  This implementation
        does nothing.  It is provided for compliance with the Python Database 
        API.  
	"""
        # this can remain implemented as "pass" 
        pass
