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

### Working with an instance
```python
# Creating a new user
user = User(username="admin", email="admin@email.com", status=1)
user.save()

# Or...
user = User()
user.username = "admin"
user.email = "admin@email.com"
user.status = 1
user.save()

# Updating an existing record
user = User.get_by_pk(pk=8)
user.email = "support@email.com"
user.save()

# Deleting a record
user = User.get_by_pk(pk=9)
user.delete()
```

## Roadmap
- Add support for methods such as `create_one` and `create_many` in the `QueryBuilder`.
- Add support for logging queries.
- Add unit tests.
- Add support for MySQL/MariaDB and PostgreSQL.
- Add support for statements like `GROUP BY` and `HAVING`.
- Add support for relationships such as one-to-one, one-to-many, and many-to-one.

Future plans include:
- Support for migrations.
- CLI tool for creating migrations and models files.

## License
[MIT](https://github.com/vcgtz/py-morgan-orm/blob/main/LICENSE)
