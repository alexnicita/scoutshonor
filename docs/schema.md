# Data schema

Early relational model for the recruiting copilot. Relationships align with MVP features for sourcing, outreach, and pipeline tracking.

## ERD overview
```
startup 1--* role 1--1 scorecard
role   1--* sequence
role   *--* candidate via stage_event
candidate 1--* profile_source
candidate 1--* interaction
candidate 1--* consent_event
candidate -- suppression_list (by contact)
```

## Entities and fields

### startup
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | until org deletion |
| name | text | Legal or brand name | yes (org identifiable) | until org deletion |
| stage | text | enum (pre-seed..public) | no | until org deletion |
| domains | json list | markets/industries | no | until org deletion |
| location | text | HQ city | no | until org deletion |
| description | text | short blurb | no | until org deletion |
| website | text | URL | no | until org deletion |
| mission | text | mission statement | no | until org deletion |
| stack | json list | tech stack | no | until org deletion |

### role
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | until org deletion |
| startup_id | text | FK startup.id | no | until org deletion |
| title | text | role title | no | until filled + 12m |
| required_skills | json list | hard requirements | no | until filled + 12m |
| nice_to_have_skills | json list | preferences | no | until filled + 12m |
| min_years_experience | integer | integer years | no | until filled + 12m |
| responsibilities | json list | key bullets | no | until filled + 12m |
| seniority | text | enum head/director/vp/cxo | no | until filled + 12m |
| location_preference | text | city/remote note | no | until filled + 12m |
| remote_ok | bool | true if remote allowed | no | until filled + 12m |
| compensation_range | text | coarse band | no | until filled + 12m |
| recruiter_notes | text | internal notes | may contain PII | minimize / redact |

### scorecard
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | role fill + 24m |
| role_id | text | FK role.id | no | role fill + 24m |
| summary | text | overall summary | no | role fill + 24m |
| must_haves | json list | hard criteria | no | role fill + 24m |
| nice_to_haves | json list | softer criteria | no | role fill + 24m |
| evaluation_points | json list | scoring rubric | no | role fill + 24m |

### candidate
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | consent revoke or 24m inactivity |
| full_name | text | Candidate name | yes | consent revoke or 24m inactivity |
| current_title | text | Current title | yes (in combo) | consent revoke or 24m inactivity |
| titles | json list | prior titles | yes (in combo) | consent revoke or 24m inactivity |
| years_experience | integer | coarse years | no | consent revoke or 24m inactivity |
| skills | json list | normalized skills | no | consent revoke or 24m inactivity |
| domains | json list | industries | no | consent revoke or 24m inactivity |
| locations | json list | cities/regions | yes (geo) | consent revoke or 24m inactivity |
| timezone | text | Olson TZ | yes (geo) | consent revoke or 24m inactivity |
| remote_preference | bool | prefers remote | no | consent revoke or 24m inactivity |
| stage_preferences | json list | job stage preferences | no | consent revoke or 24m inactivity |
| linkedin_url | text | profile link | yes | consent revoke or 24m inactivity |
| email | text | primary email | yes | consent revoke or 24m inactivity |

### profile_source
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | consent revoke or 24m inactivity |
| candidate_id | text | FK candidate.id | no | consent revoke or 24m inactivity |
| source | text | enum: linkedin/referral/manual/csv | no | consent revoke or 24m inactivity |
| handle | text | username or slug | may contain PII | consent revoke or 24m inactivity |
| url | text | source URL | may contain PII | consent revoke or 24m inactivity |
| notes | text | import notes | may contain PII | minimize; consent revoke |
| imported_at | text | ISO timestamp | no | consent revoke or 24m inactivity |

### interaction
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | consent revoke or 18m after send |
| candidate_id | text | FK candidate.id | no | consent revoke or 18m after send |
| channel | text | email/linkedin/call | no | consent revoke or 18m after send |
| direction | text | outbound/inbound | no | consent revoke or 18m after send |
| subject | text | message subject | yes | redact after 90d |
| body | text | message body | yes | redact after 90d |
| status | text | drafted/sent/delivered | no | consent revoke or 18m after send |
| outcome | text | replied/bounced/opt-out | may contain PII | redact after 90d |
| metadata | json | headers, thread ids | may contain PII | redact sensitive fields |
| occurred_at | text | ISO timestamp | no | consent revoke or 18m after send |

### sequence
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | until role archive |
| role_id | text | FK role.id | no | until role archive |
| name | text | e.g. "Eng outreach v1" | no | until role archive |
| steps | json list | offsets + channel/templates | templates may hold PII placeholders | until role archive |
| active | bool | enabled flag | no | until role archive |

### stage_event
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | consent revoke or 24m after close |
| candidate_id | text | FK candidate.id | no | consent revoke or 24m after close |
| role_id | text | FK role.id | no | consent revoke or 24m after close |
| stage | text | applied/screen/interview/offer | no | consent revoke or 24m after close |
| status | text | scheduled/passed/failed/withdrew | may contain PII in notes | consent revoke or 24m after close |
| notes | text | interviewer note ref | may contain PII | redact/summarize |
| occurred_at | text | ISO timestamp | no | consent revoke or 24m after close |

### suppression_list
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| contact | text | unique email/phone | yes | until user revokes suppression |
| reason | text | opt-out/bounce/manual | may contain PII | until user revokes suppression |
| source | text | system/manual/import | no | until user revokes suppression |
| created_at | text | ISO timestamp | no | until user revokes suppression |

### consent_event
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | audit forever |
| contact | text | email/phone | yes | audit forever (minimized) |
| candidate_id | text | optional FK candidate.id | yes | audit forever (minimized) |
| status | text | granted/withdrawn | no | audit forever |
| source | text | form/email/manual | no | audit forever |
| notes | text | proof link | may contain PII | audit forever (redacted) |
| recorded_at | text | ISO timestamp | no | audit forever |

### audit_log
| Field | Type | Notes | PII | Retention |
| --- | --- | --- | --- | --- |
| id | text | UUID | no | audit forever (minimized) |
| event_type | text | e.g. interaction_blocked | no | audit forever (minimized) |
| subject_id | text | candidate/contact/ref id | may contain PII | store hashed contact where possible |
| detail | json | redacted metadata | avoid PII | audit forever (minimized) |
| created_at | text | ISO timestamp | no | audit forever |

## Notes
- PII is minimized for logging; use `src/utils/redact.py` on any debug payloads and `suppression_list` before sends.
- Retention clocks reset on activity; anonymize or delete records on consent withdrawal.
- Array fields are stored as JSON for portability; migrations keep schema minimal until a full ORM lands.
