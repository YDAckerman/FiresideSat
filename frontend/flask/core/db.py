
import psycopg2
from flask import current_app, g

engine = create_engine(current_app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import fireside.models
    Base.metatdata.create_all(bind=engine)
