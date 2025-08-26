from sqlmodel import create_engine, Session, SQLModel

engine = create_engine("sqlite:///assessment.db")

def get_session():
    with Session(engine) as session:
        yield session
        
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)