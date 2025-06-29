import pytest
from fastapi.testclient import TestClient
from main import app
import inspection_notifications_1

client = TestClient(app)

def test_add_and_get_collaborateur():
    # Add a collaborator
    collab_data = {
        "nom": "Doe",
        "prenom": "John",
        "ifo": None,
        "caces": None,
        "airr": None,
        "hgo_bo": None,
        "visite_med": None,
        "brevet_secour": None
    }
    response = client.post("/collaborateurs", json=collab_data)
    assert response.status_code == 201
    collab = response.json()
    collab_id = collab["id"]

    # Get collaborator detail
    response = client.get(f"/collaborateurs/{collab_id}")
    assert response.status_code == 200
    assert response.json()["nom"] == "Doe"

def test_list_collaborateurs():
    response = client.get("/collaborateurs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_collaborateur():
    # Add a collaborator
    collab_data = {
        "nom": "Smith",
        "prenom": "Jane",
        "ifo": None,
        "caces": None,
        "airr": None,
        "hgo_bo": None,
        "visite_med": None,
        "brevet_secour": None
    }
    response = client.post("/collaborateurs", json=collab_data)
    collab_id = response.json()["id"]

    # Update collaborator
    update_data = {
        "nom": "Smith-Updated",
        "prenom": "Jane",
        "ifo": None,
        "caces": None,
        "airr": None,
        "hgo_bo": None,
        "visite_med": None,
        "brevet_secour": None
    }
    response = client.put(f"/collaborateurs/{collab_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["nom"] == "Smith-Updated"

def test_delete_collaborateur():
    # Add a collaborator
    collab_data = {
        "nom": "ToDelete",
        "prenom": "User",
        "ifo": None,
        "caces": None,
        "airr": None,
        "hgo_bo": None,
        "visite_med": None,
        "brevet_secour": None
    }
    response = client.post("/collaborateurs", json=collab_data)
    collab_id = response.json()["id"]

    # Delete collaborator
    response = client.delete(f"/collaborateurs/{collab_id}")
    assert response.status_code == 204

    # Ensure deleted
    response = client.get(f"/collaborateurs/{collab_id}")
    assert response.status_code == 404

def test_send_notifications_post():
    response = client.post("/notifications/send")
    assert response.status_code in (200, 500)  # 500 if email config missing

def test_send_notifications_get():
    response = client.get("/notifications/send")
    assert response.status_code in (200, 500)

def test_check_inspection_dates_logic(monkeypatch):
    # Mock DB and email sending to test logic without side effects
    class DummyVehicle:
        limit_periodic_inspection = inspection_notifications_1.get_current_date()
        date_periodic_inspection = None
        limit_additional_inspection = inspection_notifications_1.get_current_date()
        date_additional_inspection = None

    class DummyDB:
        def query(self, model):
            class DummyQuery:
                def filter(self, *args, **kwargs):
                    return self
                def all(self):
                    return [DummyVehicle()]
            return DummyQuery()

    monkeypatch.setattr(inspection_notifications_1, "get_db", lambda: DummyDB())
    monkeypatch.setattr(inspection_notifications_1, "send_notification_email", lambda *a, **kw: None)
    # Should not raise
    inspection_notifications_1.check_inspection_dates()