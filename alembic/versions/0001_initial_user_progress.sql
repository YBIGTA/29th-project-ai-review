CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_user_id VARCHAR(255) NOT NULL UNIQUE,
    nickname VARCHAR(100),
    profile_image_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE TABLE auth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auth_sessions_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    lecture_id VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    pass_status VARCHAR(2) NOT NULL DEFAULT 'NP',
    hint_used BOOLEAN NOT NULL DEFAULT FALSE,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_study_sessions_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_study_sessions_status
        CHECK (status IN ('created', 'processing', 'completed', 'failed')),
    CONSTRAINT chk_study_sessions_pass_status
        CHECK (pass_status IN ('P', 'NP'))
);

CREATE TABLE audio_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_session_id UUID NOT NULL UNIQUE,
    storage_key TEXT NOT NULL,
    original_filename VARCHAR(255),
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT,
    duration_seconds NUMERIC(10, 3),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audio_files_session
        FOREIGN KEY (study_session_id) REFERENCES study_sessions(id) ON DELETE CASCADE,
    CONSTRAINT chk_audio_files_size
        CHECK (file_size IS NULL OR file_size >= 0),
    CONSTRAINT chk_audio_files_duration
        CHECK (duration_seconds IS NULL OR duration_seconds >= 0)
);

CREATE TABLE transcriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_session_id UUID NOT NULL UNIQUE,
    audio_file_id UUID NOT NULL UNIQUE,
    raw_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    stt_model VARCHAR(100) NOT NULL,
    beam_size INTEGER NOT NULL,
    correction_model VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transcriptions_session
        FOREIGN KEY (study_session_id) REFERENCES study_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_transcriptions_audio
        FOREIGN KEY (audio_file_id) REFERENCES audio_files(id) ON DELETE CASCADE,
    CONSTRAINT chk_transcriptions_beam_size
        CHECK (beam_size > 0)
);

CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_session_id UUID NOT NULL UNIQUE,
    transcription_id UUID NOT NULL UNIQUE,
    accuracy_score NUMERIC(5, 2) NOT NULL,
    coverage_score NUMERIC(5, 2) NOT NULL,
    structural_score NUMERIC(5, 2) NOT NULL,
    total_score NUMERIC(5, 2) NOT NULL,
    pass_status VARCHAR(2) NOT NULL,
    evaluation_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluations_session
        FOREIGN KEY (study_session_id) REFERENCES study_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_evaluations_transcription
        FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE,
    CONSTRAINT chk_evaluations_accuracy
        CHECK (accuracy_score BETWEEN 0 AND 40),
    CONSTRAINT chk_evaluations_coverage
        CHECK (coverage_score BETWEEN 0 AND 40),
    CONSTRAINT chk_evaluations_structural
        CHECK (structural_score BETWEEN 0 AND 20),
    CONSTRAINT chk_evaluations_total
        CHECK (total_score BETWEEN 0 AND 100),
    CONSTRAINT chk_evaluations_pass_status
        CHECK (pass_status IN ('P', 'NP'))
);

CREATE INDEX idx_study_sessions_user_created_at
    ON study_sessions(user_id, created_at DESC);

CREATE INDEX idx_auth_sessions_user_id
    ON auth_sessions(user_id);

CREATE INDEX idx_auth_sessions_active
    ON auth_sessions(session_token_hash, expires_at)
    WHERE revoked_at IS NULL;

CREATE OR REPLACE FUNCTION refresh_study_session_pass_status()
RETURNS TRIGGER AS $$
DECLARE
    target_session_id UUID;
BEGIN
    target_session_id := COALESCE(NEW.study_session_id, OLD.study_session_id);

    UPDATE study_sessions
    SET pass_status = CASE
        WHEN EXISTS (
            SELECT 1 FROM evaluations
            WHERE study_session_id = target_session_id
              AND pass_status = 'P'
        ) THEN 'P'
        ELSE 'NP'
    END
    WHERE id = target_session_id;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_refresh_study_session_pass_status
AFTER INSERT OR UPDATE OF study_session_id, pass_status OR DELETE
ON evaluations
FOR EACH ROW
EXECUTE FUNCTION refresh_study_session_pass_status();
