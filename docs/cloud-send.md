# Cloud send guardrail

GitHub Actions now sets `FEISHU_SEND_MODE=bot` for scheduled runs.
That keeps the briefing sender independent from any user login state and makes the cron job behave the same every time.

If you need to send as a user locally, unset `FEISHU_SEND_MODE` or set it to `user`.
