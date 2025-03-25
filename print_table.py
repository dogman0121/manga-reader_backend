from app import db
from app.manga.models import Poster
from manage import app

from sqlalchemy import text

with app.app_context():
    print(db.session.execute(text("""SELECT c.column_name, c.data_type
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
  AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = 'manga_poster';""")).all())

    #db.session.execute(text("ALTER TABLE manga_poster ADD PRIMARY KEY (uuid)"))
    #db.session.execute(text("ALTER TABLE manga_poster DROP CONSTRAINT manga_poster_pkey;"))
    #db.session.commit()