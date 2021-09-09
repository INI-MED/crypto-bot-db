from flask_script import Manager
from db_api import app, db
from flask_migrate import Migrate, MigrateCommand

from db_config import PG_USER, PG_PASS, PG_PORT, PG_NAME, HOST

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{HOST}:{PG_PORT}/{PG_NAME}"
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()
