import os

from cement.utils import fs

from db.database import DB
from db.tables import Repositories

from ..main import App


def extend_tinydb(app: App):
    app.log.debug("Extend app with TinyDB")

    db_file = app.config.get("warhammer40k", "db")["file"]

    # ensure that we expand the full path
    db_file = fs.abspath(db_file)
    app.log.debug("tinydb database file is: %s" % db_file)

    # ensure our parent directory exists
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db = DB(db_file)
    app.extend("db", db)
    app.extend("repositories", db.table(Repositories))
