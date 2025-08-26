import os
from typing import Generator

import pytest
from sqlmodel import SQLModel, Session, create_engine

TEST_DB_URL = "sqlite:///./assessment_test.db"


@pytest.fixture(scope="function")
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )

    # Fresh tables for each test function
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as s:
        yield s

    # Cleanup DB file after each test to avoid residue
    try:
        if os.path.exists("assessment_test.db"):
            os.remove("assessment_test.db")
    except Exception:
        # Best-effort cleanup; ignore errors
        pass
