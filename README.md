# SimpleCatalog
###Built-from-scratch web server using Object Relational Mapping for performing CRUD operations on a SQLite database.
####Contents:
<ul>
<li>database_setup.py creates the database and class definitions for Object Relational Mapping using SQLAlchemy. This avoids having to using SQL statements in Python code.
<li>lotsofmenus.py populates the database with restaurant data.
<li>webserver.py is built-from-scratch, handling GET & POST requests for performing CRUD operations on the database. 
</ul>
####To create and populate a local database, SQLAlchemy must be installed. Then from a terminal run:
```
> python database_setup.py
> python lotsofmenus.py
```
####To run the server locally, from the terminal run:
```
> python webserver.py
```
and then open a browser and enter the url 'localhost:8080/restaurants'
