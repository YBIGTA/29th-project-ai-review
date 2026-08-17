from fastapi.testclient import TestClient

from backend.app import main


def test_review_accepts_stt_result_and_returns_mock_evaluation():
    client = TestClient(main.create_app())
    response = client.post(
        "/api/reviews/submit",
        json={
            "session_id": "db-session-01",
            "topic": "DB",
            "transcript_raw": "raw transcript",
            "transcript_corrected": "corrected transcript",
            "term_db_used": {"safe": [], "content_word_collision": [], "particle_collision": []},
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
        json={"session_id": "db-session-01", "topic": "DB"},
    )
    assert response.status_code == 422
