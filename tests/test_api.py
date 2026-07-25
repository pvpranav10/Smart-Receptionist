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
