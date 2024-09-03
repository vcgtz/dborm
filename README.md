# Morgan ORM for Python
A simple and easy-to-use ORM for managing your database queries.

## Motivation
I decided to create an ORM for two main reasons:
- To build an ORM that is extremely simple to use, without complex configurations—just set up your database access and you're ready to go.
- As a learning experience to understand how an ORM works internally.

I've worked with Laravel for many years, so in a way, I'm drawing inspiration from Eloquent for this ORM.

## Usage
### Using the query builder from a model

Creating a model
```python
# Import required packages
from morgan.connection import DatabaseConfig, ConnectionType
from morgan.orm import Model

# Create your model inheriting from Model
class User(Model):
    table = "users"     # Name of your table
    primary_key = "id"  # Name of your primary key

    # Configuration for the database (now it only supports SQLite)
    db_config = DatabaseConfig(connector=ConnectionType.SQLite, database_url="morgan.db")
```

Some available operations
```python
# Get all the users
users = User.all()

# Get user by primary key
user = User.get_by_pk(pk=92)

# Get users by filtering results
users = User.where("status = ?", 1).get()

# Limiting results
users = User.where("status = ?", 1).limit(5).get()

# Ordering results
users = User.where("status = ?", 1).order_by("created_at", "DESC").get()

# Updating records
User.where("status = ?", 0).update("status = ?", 1).exec()

# Deleting records
User.where("email = ?", "user@email.com").delete().exec()
```

## Roadmap
- Implement basic CRUD operations (Create, Read, Update, Delete).
- Add support for simple relationships such as one-to-one and one-to-many.
- Integrate more SQL clauses.

Future plans include:
- Support for migrations.
- CLI for creating migrations and models.
- Integration with additional databases like MySQL/MariaDB and PostgreSQL.

## License
[MIT](https://github.com/vcgtz/py-morgan-orm/blob/main/LICENSE)
