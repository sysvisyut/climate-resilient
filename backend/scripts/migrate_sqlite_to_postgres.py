#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Ensure 'backend' is on sys.path so we can import app.* regardless of CWD
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Import your existing Base and models so metadata is complete
from app.models.database import Base
from app.models import models as m

# Searchable placeholders for RDS
# TODO_FILL_RDS_HOST
# TODO_FILL_RDS_PORT
# TODO_FILL_RDS_DB
# TODO_FILL_RDS_USER
# TODO_FILL_RDS_PASSWORD

SQLITE_PATH = "/Users/hari/Project buffer/climate-resilient-aws/backend/climate_health.db"  # TODO_FILL_SQLITE_PATH_IF_DIFFERENT
SQLITE_URL = f"sqlite:///{SQLITE_PATH}"

DATABASE_URL = os.environ.get("DATABASE_URL")

sqlite_engine = create_engine(SQLITE_URL)
pg_engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SQLiteSession = sessionmaker(bind=sqlite_engine, autocommit=False, autoflush=False)
PGSession = sessionmaker(bind=pg_engine, autocommit=False, autoflush=False)


def rows_as_dicts(session, model_cls):
    cols = [c.name for c in model_cls.__table__.columns]
    for (obj,) in session.execute(select(model_cls)).yield_per(1000):
        yield {c: getattr(obj, c) for c in cols}


def copy_table(sqlite_session, pg_session, model_cls, table_name):
    print(f"Copying {table_name} ...")
    data = list(rows_as_dicts(sqlite_session, model_cls))
    if not data:
        print(f"{table_name}: no rows.")
        return
    pg_session.execute(model_cls.__table__.insert(), data)
    pg_session.commit()
    print(f"{table_name}: inserted {len(data)} rows.")


def fix_sequence(pg_session, table_name, pk_col="id"):
    sql = text(
        "SELECT setval(pg_get_serial_sequence(:t, :c), COALESCE(MAX("
        + pk_col
        + "), 1), true) FROM "
        + table_name
    )
    pg_session.execute(sql, {"t": table_name, "c": pk_col})
    pg_session.commit()


def main():
    # Create schema on Postgres per your SQLAlchemy models
    Base.metadata.create_all(bind=pg_engine)

    with SQLiteSession() as s_src, PGSession() as s_dst:
        # Order matters due to FKs
        copy_table(s_src, s_dst, m.Location, "locations")
        copy_table(s_src, s_dst, m.ClimateData, "climate_data")
        copy_table(s_src, s_dst, m.HealthData, "health_data")
        copy_table(s_src, s_dst, m.HospitalData, "hospital_data")
        copy_table(s_src, s_dst, m.User, "users")

        # Fix sequences so future inserts don’t collide
        for t in ["locations", "climate_data", "health_data", "hospital_data", "users"]:
            fix_sequence(s_dst, t, "id")

    print("Migration completed successfully.")


if __name__ == "__main__":
    main()


