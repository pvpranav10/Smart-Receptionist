import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_patient_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyClinikoClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

        async def create_patient(self, payload: dict[str, object]) -> dict[str, object]:
            return {
                "patient": {
                    "id": 42,
                    "first_name": payload.get("first_name", ""),
                    "last_name": payload.get("last_name", ""),
                    "email": payload.get("email"),
                }
            }

        async def close(self) -> None:
            return None

    monkeypatch.setattr("app.api.patients.ClinikoClient", DummyClinikoClient)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/patients",
            json={"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "patient_id": 42,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": None,
        "raw_data": {
            "id": 42,
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
        },
    }


@pytest.mark.asyncio
async def test_initiated_endpoint_calls_bolna_client(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyClinikoClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

        async def list_patients(self) -> dict[str, object]:
            return {
                "patients": [
                    {
                        "id": 7,
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "email": "jane@example.com",
                        "phone": "+123456789",
                    }
                ]
            }

        async def close(self) -> None:
            return None

    class DummyBolnaClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs
            self.calls: list[dict[str, object]] = []

        async def initiate_user_variables_bolna(self, payload: dict[str, object]) -> dict[str, object]:
            self.calls.append(payload)
            return {"status": "ok"}

    bolna_client = DummyBolnaClient()

    monkeypatch.setattr("app.main.ClinikoClient", DummyClinikoClient)
    monkeypatch.setattr("app.main.BolnaClient", lambda *args, **kwargs: bolna_client)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/intiated",
            json={"phone_number": "+123456789", "agent_id": "agent-123"},
        )

    assert response.status_code == 200
    assert bolna_client.calls[0]["recipient_phone_number"] == "+123456789"
    assert bolna_client.calls[0]["user_data"]["customer_name"] == "Jane Doe"
