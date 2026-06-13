from sqlmodel import create_engine
from sqlalchemy import text


DATABASE_URL = (
    "sqlite:///database.db"
)

engine = create_engine(
    DATABASE_URL
)


def migrate():

    migrations = [

        """
        ALTER TABLE userprofile
        ADD COLUMN is_adult
        INTEGER DEFAULT 0
        """

    ]

    with engine.connect() as conn:

        for sql in migrations:

            try:

                conn.execute(
                    text(sql)
                )

                conn.commit()

            except Exception:

                pass