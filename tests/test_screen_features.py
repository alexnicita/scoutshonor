from src.features.screen.ats_sync import AtsSync
from src.features.screen.parser import ResumeParser
from src.features.screen.summary import summarize_candidate


def load_resume_text() -> str:
    with open("tests/fixtures/resume_sample.txt", encoding="utf-8") as f:
        return f.read()


def test_resume_parser_extracts_core_fields():
    parser = ResumeParser()
    profile = parser.parse(load_resume_text())

    assert profile.full_name == "Avery Johnson"
    assert profile.email == "avery.johnson@example.com"
    assert profile.phone.startswith("415-555")
    assert "python" in profile.skills
    assert profile.years_experience == 8


def test_summary_risks_and_ats_sync_dry_run():
    parser = ResumeParser()
    profile = parser.parse(load_resume_text())
    summary = summarize_candidate(profile, required_skills=["python", "kubernetes"])

    assert any("kubernetes" in risk for risk in summary.risks)
    assert "years experience" in summary.summary

    ats = AtsSync()
    result = ats.push_note(candidate_id="cand-001", risk_summary=summary)

    assert result.dry_run is True
    assert result.delivered is False
    assert "Summary:" in result.note
    assert ats.pushed[0].candidate_id == "cand-001"
