from src.integrations.slack_app import SlackApp


def test_slack_app_dry_run_posts_message():
    app = SlackApp(bot_token="xoxb-test", dry_run=True)
    result = app.post_message(channel="C123", text="hello")
    assert result["dry_run"] is True
    assert result["payload"]["channel"] == "C123"


def test_slash_commands_return_responses():
    app = SlackApp(bot_token="xoxb-test", dry_run=True)
    resp = app.handle_slash_command(action="draft-outreach", text="backend role", user_id="U1", channel_id="C1")
    assert "outreach" in resp.text
    resp2 = app.handle_slash_command(action="who-is-stuck", text="", user_id="U1", channel_id="C1")
    assert "Roles in-flight" in resp2.text
