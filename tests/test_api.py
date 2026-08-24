from fastapi.testclient import TestClient

from backend.app import main
from backend.app.integrations import mock_evaluation


def test_review_accepts_stt_result_and_returns_evaluation(monkeypatch):
    monkeypatch.setattr(
        main,
        "evaluate_selected_topic",
        lambda **kwargs: mock_evaluation(kwargs["transcript"]),
    )
    client = TestClient(main.create_app())
    response = client.post(
        "/api/reviews/submit",
        json={
            "session_id": "db-session-01",
            "topic": "기초통계",
            "lecture_id": "basic_statistics",
            "objective_id": "stats.hypothesis_uncertainty",
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
    assert body["objective_id"] == "stats.hypothesis_uncertainty"
    assert body["quantitative"]["scores"]["essential"]["max_score"] == 60
    assert body["quantitative"]["scores"]["supporting"]["max_score"] == 20
    assert body["quantitative"]["scores"]["coverage"]["max_score"] == 20
    assert body["qualitative"]["missing_claims"]


def test_review_requires_stt_result_fields():
    client = TestClient(main.create_app())
    response = client.post(
        "/api/reviews/submit",
        json={"session_id": "db-session-01", "topic": "DB"},
    )
    assert response.status_code == 422
