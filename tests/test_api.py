# tests/test_api.py
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db, engine, SessionLocal
from app.models import Bank, Branch

# 👇 Force app to use in-memory SQLite before anything else
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def client():
    # Recreate schema in fresh in-memory DB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed minimal data
    with SessionLocal() as db:
        sbi = Bank(id=1, name="STATE BANK OF INDIA")
        db.add(sbi)
        db.add(Branch(
            ifsc="SBIN0000001",
            bank_id=1,
            branch="MUMBAI",
            address="FORT",
            city="MUMBAI",
            district="MUMBAI",
            state="MAHARASHTRA",
        ))
        db.commit()

    # Override get_db to always yield from SessionLocal
    def override_get_db():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_list_banks(client):
    resp = client.get("/banks")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "STATE BANK OF INDIA"


def test_get_branch(client):
    resp = client.get("/branches/SBIN0000001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ifsc"] == "SBIN0000001"
    assert data["bank"]["name"] == "STATE BANK OF INDIA"


def test_list_branches_for_bank(client):
    resp = client.get("/banks/1/branches")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["ifsc"] == "SBIN0000001"


def test_get_branch_not_found(client):
    resp = client.get("/branches/INVALID123")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Branch not found"


def test_graphql_query(client):
    query = """
    query {
      branches(limit: 1) {
        total
        items {
          ifsc
          branch
          bank {
            name
          }
        }
      }
    }
    """
    resp = client.post("/gql", json={"query": query})
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["data"]["branches"]["items"][0]["ifsc"] == "SBIN0000001"
