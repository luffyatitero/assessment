import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from main import app
from db import get_session

# Try to import router if endpoints exist; safe if empty
try:
	from routes import router as api_router  # type: ignore
	app.include_router(api_router)
except Exception:
	pass


TEST_DB_URL = "sqlite:///./assessment_api_test.db"


def _build_test_engine():
	return create_engine(
		TEST_DB_URL,
		connect_args={"check_same_thread": False},
	)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
	engine = _build_test_engine()

	# Fresh tables for each test
	SQLModel.metadata.drop_all(engine)
	SQLModel.metadata.create_all(engine)

	def override_get_session() -> Generator[Session, None, None]:
		with Session(engine) as session:
			yield session

	# Override the app's DB dependency
	app.dependency_overrides[get_session] = override_get_session

	with TestClient(app) as c:
		yield c

	# Cleanup DB file after each test to avoid residue
	try:
		if os.path.exists("assessment_api_test.db"):
			os.remove("assessment_api_test.db")
	except Exception:
		pass


def test_root_ok(client: TestClient):
	resp = client.get("/")
	assert resp.status_code == 200
	assert resp.json() == {"message": "Hello, World!"}


# Below are route-contract tests for future CRUD endpoints.
# They are marked xfail until the corresponding endpoints are implemented.


@pytest.mark.xfail(reason="POST /users not implemented yet")
def test_create_user(client: TestClient):
	payload = {
		"submitted_by": "tester",
		"user_type": "student",
		"full_name": "Alice Doe",
		"username": "alice",
		"email": "alice@example.com",
		"password": "secret",
	}
	resp = client.post("/users", json=payload)
	assert resp.status_code == 201
	data = resp.json()
	assert data["id"] > 0
	assert data["username"] == "alice"


@pytest.mark.xfail(reason="GET /users/{id} not implemented yet")
def test_get_user_by_id(client: TestClient):
	created = client.post(
		"/users",
		json={
			"submitted_by": "tester",
			"user_type": "student",
			"full_name": "Bob Doe",
			"username": "bob",
			"email": "bob@example.com",
			"password": "secret",
		},
	)
	user_id = created.json()["id"]
	resp = client.get(f"/users/{user_id}")
	assert resp.status_code == 200
	assert resp.json()["id"] == user_id


@pytest.mark.xfail(reason="PATCH /users/{id} not implemented yet")
def test_update_user(client: TestClient):
	created = client.post(
		"/users",
		json={
			"submitted_by": "tester",
			"user_type": "student",
			"full_name": "Carol Smith",
			"username": "carol",
			"email": "carol@example.com",
			"password": "secret",
		},
	)
	user_id = created.json()["id"]
	resp = client.patch(f"/users/{user_id}", json={"full_name": "Carol S."})
	assert resp.status_code == 200
	assert resp.json()["full_name"] == "Carol S."


@pytest.mark.xfail(reason="DELETE /users/{id} not implemented yet")
def test_delete_user(client: TestClient):
	created = client.post(
		"/users",
		json={
			"submitted_by": "tester",
			"user_type": "student",
			"full_name": "Dave Doe",
			"username": "dave",
			"email": "dave@example.com",
			"password": "secret",
		},
	)
	user_id = created.json()["id"]
	resp = client.delete(f"/users/{user_id}")
	assert resp.status_code == 204


@pytest.mark.xfail(reason="CRUD for departments not implemented yet")
def test_departments_crud_contract(client: TestClient):
	# Create
	create_resp = client.post("/departments", json={"submitted_by": "tester", "department_name": "Physics"})
	assert create_resp.status_code in (201,)
	dept = create_resp.json()
	dept_id = dept["id"]

	# Read
	get_resp = client.get(f"/departments/{dept_id}")
	assert get_resp.status_code == 200
	assert get_resp.json()["department_name"] == "Physics"

	# Update
	update_resp = client.patch(f"/departments/{dept_id}", json={"department_name": "Astrophysics"})
	assert update_resp.status_code == 200
	assert update_resp.json()["department_name"] == "Astrophysics"

	# Delete
	delete_resp = client.delete(f"/departments/{dept_id}")
	assert delete_resp.status_code == 204


@pytest.mark.xfail(reason="CRUD for courses not implemented yet")
def test_courses_crud_contract(client: TestClient):
	# Needs an existing department
	dept_resp = client.post("/departments", json={"submitted_by": "tester", "department_name": "CS"})
	dept_id = dept_resp.json()["id"]

	create_resp = client.post(
		"/courses",
		json={
			"submitted_by": "tester",
			"course_name": "Algorithms",
			"department_id": dept_id,
			"semester": "Fall",
			"class_id": 101,
			"lecture_hours": 3,
		},
	)
	assert create_resp.status_code == 201
	course = create_resp.json()
	course_id = course["id"]

	get_resp = client.get(f"/courses/{course_id}")
	assert get_resp.status_code == 200

	update_resp = client.patch(f"/courses/{course_id}", json={"lecture_hours": 4})
	assert update_resp.status_code == 200
	assert update_resp.json()["lecture_hours"] == 4

	delete_resp = client.delete(f"/courses/{course_id}")
	assert delete_resp.status_code == 204


@pytest.mark.xfail(reason="CRUD for students not implemented yet")
def test_students_crud_contract(client: TestClient):
	# Pre-reqs: user and department
	user_resp = client.post(
		"/users",
		json={
			"submitted_by": "tester",
			"user_type": "student",
			"full_name": "Eve Doe",
			"username": "eve",
			"email": "eve@example.com",
			"password": "secret",
		},
	)
	user_id = user_resp.json()["id"]
	dept_resp = client.post("/departments", json={"submitted_by": "tester", "department_name": "Math"})
	dept_id = dept_resp.json()["id"]

	create_resp = client.post(
		"/students",
		json={
			"submitted_by": "tester",
			"user_id": user_id,
			"department_id": dept_id,
			"class_id": 1,
		},
	)
	assert create_resp.status_code == 201
	student = create_resp.json()
	student_id = student["id"]

	get_resp = client.get(f"/students/{student_id}")
	assert get_resp.status_code == 200

	update_resp = client.patch(f"/students/{student_id}", json={"class_id": 2})
	assert update_resp.status_code == 200
	assert update_resp.json()["class_id"] == 2

	delete_resp = client.delete(f"/students/{student_id}")
	assert delete_resp.status_code == 204


@pytest.mark.xfail(reason="CRUD for attendance logs not implemented yet")
def test_attendance_logs_crud_contract(client: TestClient):
	# Pre-reqs
	dept_resp = client.post("/departments", json={"submitted_by": "tester", "department_name": "EE"})
	dept_id = dept_resp.json()["id"]
	course_resp = client.post(
		"/courses",
		json={
			"submitted_by": "tester",
			"course_name": "Circuits",
			"department_id": dept_id,
			"semester": "Spring",
			"class_id": 7,
			"lecture_hours": 3,
		},
	)
	course_id = course_resp.json()["id"]

	user_resp = client.post(
		"/users",
		json={
			"submitted_by": "tester",
			"user_type": "student",
			"full_name": "Frank Doe",
			"username": "frank",
			"email": "frank@example.com",
			"password": "secret",
		},
	)
	user_id = user_resp.json()["id"]
	student_resp = client.post(
		"/students",
		json={
			"submitted_by": "tester",
			"user_id": user_id,
			"department_id": dept_id,
			"class_id": 7,
		},
	)
	student_id = student_resp.json()["id"]

	create_resp = client.post(
		"/attendance-logs",
		json={
			"submitted_by": "tester",
			"student_id": student_id,
			"course_id": course_id,
			"present": True,
		},
	)
	assert create_resp.status_code == 201
	log_id = create_resp.json()["id"]

	get_resp = client.get(f"/attendance-logs/{log_id}")
	assert get_resp.status_code == 200

	update_resp = client.patch(f"/attendance-logs/{log_id}", json={"present": False})
	assert update_resp.status_code == 200
	assert update_resp.json()["present"] is False

	delete_resp = client.delete(f"/attendance-logs/{log_id}")
	assert delete_resp.status_code == 204
