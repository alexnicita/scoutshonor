from src.obs.logging import configure_logging, get_logger


def test_structured_logger_appends_context(caplog):
    configure_logging(level="INFO")
    logger = get_logger("obs-test", request_id="req-123")

    with caplog.at_level("INFO"):
        logger.info("event-logged", extra={"user_id": 42})

    combined = " ".join(caplog.messages)
    assert "event-logged" in combined
    assert "request_id=req-123" in combined
    assert "user_id=42" in combined
