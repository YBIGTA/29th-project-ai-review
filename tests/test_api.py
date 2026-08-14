from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_material_upload_and_mock_review(tmp_path):
    client = TestClient(create_app(tmp_path))
    pdf = b"%PDF-1.7\nmock material\n%%EOF"

    upload_response = client.post(
        "/api/materials/upload",
        files={"pdf_file": ("lecture.pdf", pdf, "application/pdf")},
    )

    assert upload_response.status_code == 201
    upload_body = upload_response.json()
    pdf_id = upload_body["pdf_id"]
    assert upload_body["filename"] == "lecture"
    assert upload_body["status"] == "processing"
    assert "분석" in upload_body["message"]
    assert (tmp_path / "materials" / f"{pdf_id}.pdf").is_file()

    processing_response = client.get(f"/api/materials/{pdf_id}/status")
    assert processing_response.status_code == 200
    processing_body = processing_response.json()
    assert processing_body["pdf_id"] == pdf_id
    assert processing_body["filename"] == "lecture"
    assert processing_body["status"] == "completed"

    review_response = client.post(
        "/api/reviews/submit",
        data={"pdf_id": pdf_id},
        files={"audio_file": ("answer.webm", b"mock audio", "audio/webm")},
    )

    assert review_response.status_code == 201
    body = review_response.json()
    assert body["pdf_id"] == pdf_id
    assert body["status"] == "mock"
    assert body["score"] == 78
    assert body["feedback"]["summary"]
    assert (tmp_path / "audio" / body["audio_filename"]).is_file()


def test_review_requires_existing_material(tmp_path):
    client = TestClient(create_app(tmp_path))

    response = client.post(
        "/api/reviews/submit",
        data={"pdf_id": "missing"},
        files={"audio_file": ("answer.wav", b"mock audio", "audio/wav")},
    )

    assert response.status_code == 404


def test_material_rejects_non_pdf(tmp_path):
    client = TestClient(create_app(tmp_path))

    response = client.post(
        "/api/materials/upload",
        files={"pdf_file": ("notes.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 415


def test_material_status_requires_existing_pdf(tmp_path):
    client = TestClient(create_app(tmp_path))

    response = client.get("/api/materials/missing/status")

    assert response.status_code == 404
