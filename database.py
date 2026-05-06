from sqlalchemy import create_engine
DATABASE_URL = 'postgresql://awanitraj@localhost:5432/retail_db'
engine = create_engine(DATABASE_URL)