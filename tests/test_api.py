from fastapi.testclient import TestClient

from backend.app import main


def test_review_accepts_stt_result_and_returns_mock_evaluation():
    client = TestClient(main.create_app())
    response = client.post(
        "/api/reviews/submit",
        json={
            "review_id": "review-1",
            "session_id": "db-session-01",
            "transcript": "raw transcript",
            "corrected_transcript": "corrected transcript",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["transcript"] == "raw transcript"
    assert body["corrected_transcript"] == "corrected transcript"
    assert body["status"] == "mock"
    assert body["session_id"] == "db-session-01"


def test_review_requires_stt_result_fields():
    client = TestClient(main.create_app())
    response = client.post(
        "/api/reviews/submit",
        json={"review_id": "review-1", "session_id": "db-session-01"},
    )
    assert response.status_code == 422
