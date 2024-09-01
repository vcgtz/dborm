# Morgan ORM for Python
A simple and easy-to-use ORM for managing your database queries.

## Motivation
I decided to create an ORM for two main reasons:
- To build an ORM that is extremely simple to use, without complex configurations—just set up your database access and you're ready to go.
- As a learning experience to understand how an ORM works internally.

I've worked with Laravel for many years, so in a way, I'm drawing inspiration from Eloquent for this ORM.

## What I Expect to Achieve
Here's how I envision Morgan ORM working once the first version is released:
```python
# Importing the base class for models
from morgan.orm import Model

# Defining the database connection
db_connection = {
    "connector": "sqlite",
    "database": "development.db"
}

# Example for connecting to MySQL
db_connection = {
    "connector": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "username": "admin",
    "password": "p4ssw0rd",
    "database": "development"
}

# Creating a model
class User(Model):
    table = "users"
    primary_key = "id"
    connection = db_connection

# Querying the database using the User model
# Each user or record will be an instance of the User class
admin_users = User.where("role = ?", "admin").order_by("created_at", "DESC").get()
active_users = User.where("active = ?", True).limit(5).get()
current_user = User.get_by_pk(pk=23)
all_users = User.all()

# Creating new users
user = User.create(username="vcgtz", email="my-email@email.com", password="********")

# Creating, updating, and even deleting users
user = User(username="vcgtz", email="my-email@email.com", password="********")
user.save()  # Save the new user
user.email = "my-new-email@email.com"
user.save()  # Update the user's email
user.delete()  # Delete the user
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
