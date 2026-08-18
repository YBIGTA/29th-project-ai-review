from fastapi.testclient import TestClient

from backend.app import main
from backend.app.integrations import mock_evaluation


def test_review_accepts_stt_result_and_returns_evaluation(monkeypatch):
    monkeypatch.setattr(
        main,
        "evaluate_with_rag",
        lambda **kwargs: mock_evaluation(kwargs["transcript"]),
    )
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
    assert body["status"] == "evaluated"
    assert body["session_id"] == "db-session-01"
    assert body["quantitative"]["scores"]["accuracy"]["max_score"] == 40
    assert body["quantitative"]["scores"]["coverage"]["max_score"] == 40
    assert body["quantitative"]["scores"]["structural_understanding"]["max_score"] == 20
    assert body["qualitative"]["missing_concepts"]


def test_review_requires_stt_result_fields():
    client = TestClient(main.create_app())
    response = client.post(
        "/api/reviews/submit",
        json={"session_id": "db-session-01", "topic": "DB"},
    )
    assert response.status_code == 422
