from sqlalchemy import create_engine, URL , text
from sqlalchemy.orm import sessionmaker, declarative_base
from settings.config import secret
from sqlalchemy_utils import database_exists, create_database

# database connection code here

db_url= URL.create(
    drivername= 'postgresql',
    database= secret.database,
    username= secret.dbuser,
    password= secret.password,
    host= secret.host,
    port= secret.port
)

engine= create_engine(db_url, pool_pre_ping= True)

# create db if not exist
if not database_exists(engine.url):
    create_database(engine.url)
    print('----- Database created! -----')

session_local= sessionmaker(autocommit= False, autoflush= False, bind= engine)
Base= declarative_base()

def get_db():
    db= session_local()
    try:
        yield db
    finally:
        db.close()

try:
    db= session_local()
    db.execute(text('SELECT 1'))
    print('\n----- Connected to db! -----')
except Exception as e:
    print('\n----- Connection failed! ERROR : ', e)


