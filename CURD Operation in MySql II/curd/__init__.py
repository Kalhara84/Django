# curd/__init__.py - makes the "curd" folder a Python package (settings, urls, wsgi, asgi live here).
#
# Use PyMySQL as the MySQL driver. Django looks for "MySQLdb", so this line
# makes PyMySQL pretend to be it. It must run before Django connects to MySQL.
import pymysql

pymysql.install_as_MySQLdb()
