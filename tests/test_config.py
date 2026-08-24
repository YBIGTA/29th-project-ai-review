from dataclasses import replace

from src.config import LECTURES, Settings, resolve_pdf_path


def test_resolve_pdf_path_supports_existing_korean_filename(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pdf = data_dir / "기초통계.pdf"
    pdf.write_bytes(b"pdf")
    settings = replace(
        Settings.from_env(),
        project_root=tmp_path,
        raw_data_dir=data_dir / "raw",
        legacy_data_dir=data_dir,
    )

    assert resolve_pdf_path(settings, LECTURES["basic_statistics"]) == pdf


def test_resolve_pdf_path_supports_pdfs_subdirectory(tmp_path):
    data_dir = tmp_path / "data"
    pdf_dir = data_dir / "pdfs"
    pdf_dir.mkdir(parents=True)
    pdf = pdf_dir / "CS기초.pdf"
    pdf.write_bytes(b"pdf")
    settings = replace(
        Settings.from_env(),
        project_root=tmp_path,
        raw_data_dir=data_dir / "raw",
        legacy_data_dir=data_dir,
    )

    assert resolve_pdf_path(settings, LECTURES["cs_basics"]) == pdf


def test_all_expected_pdf_files_are_resolvable():
    settings = Settings.from_env()

    for lecture in LECTURES.values():
        assert resolve_pdf_path(settings, lecture).is_file()
