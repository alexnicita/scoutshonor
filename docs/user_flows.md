# User Flows

## Outreach
1. Recruiter selects candidate + role and chooses a tone profile.
2. Sequence engine schedules intro + follow-up (48h) with reply suppression.
3. Any reply is routed to the owner; metrics hook records `reply_routed`.

## Screening
1. Upload or paste plaintext resume into the parser.
2. Parser extracts contact, skills, and years; summary module flags risks vs. required skills.
3. ATS sync composes a note (dry-run) for review before posting.

## Pilot Coordination
1. Prep demo data; confirm instrumentation checklist.
2. Run joint sessions with recruiters/hiring managers.
3. Capture feedback using the template and file issues with owners.
