# Tutor UserOps Plugin (Tutor v20.x / Open edX Teak)

This repository contains:

1. **Tutor plugin package**: `tutor_userops`
2. **Django app package**: `userops`

It installs a staff-only API in LMS to:

- Preview users filtered by `UserProfile.meta` JSON content.
- Bulk enroll matching users into one or more courses by forwarding to Open edX built-in bulk enrollment API logic.

## How it works

- User metadata is read from `common.djangoapps.student.models.UserProfile.meta` (a `TextField`).
- Filtering is done **in Python** by parsing JSON safely (`invalid/empty => {}`).
- Filters are applied against `meta["org"]` using case-insensitive, trimmed string comparison.
- Matching users are converted to email identifiers (users with empty email are skipped).
- Enrollment is forwarded to Open edX `BulkEnrollView` (no custom enrollment DB writes).

## API Endpoints

All endpoints are LMS endpoints and require `request.user.is_staff == True`.

### 1) Preview users by metadata

`POST /api/userops/v1/users/preview`

Request:

```json
{
  "filters": {"cluster": "NORTH 1", "asm_1": "ASM1"},
  "limit": 50
}
```

Response:

```json
{
  "count": 123,
  "sample": [
    {
      "username": "demo",
      "email": "demo@example.com",
      "org": {"cluster": "NORTH 1", "asm_1": "ASM1"}
    }
  ]
}
```

### 2) Bulk enroll by metadata

`POST /api/userops/v1/bulk-enroll/by-metadata`

Request:

```json
{
  "filters": {"cluster": "NORTH 1", "asm_1": "ASM1"},
  "courses": ["course-v1:edX+Demo+123", "course-v1:edX+Demo2+456"],
  "cohorts": ["cohortA", "cohortB"],
  "action": "enroll",
  "auto_enroll": true,
  "email_students": false
}
```

Response:

```json
{
  "matched_users": 123,
  "used_identifiers": 120,
  "skipped_no_email": 3,
  "upstream_status": 200,
  "upstream_body": {"...": "response from bulk enroll"}
}
```

Validation highlights:

- `courses` required and non-empty.
- `action` must be `enroll` or `unenroll`.
- If `cohorts` is provided and non-empty, its length must match `courses` length.

## Installation (Tutor)

From this repository root:

```bash
pip install -e .
tutor plugins enable userops
```

Then rebuild/restart Open edX image so plugin files are pip-installed into the LMS container:

```bash
tutor images build openedx
tutor local launch
```

## Tutor plugin integration details

The plugin registers:

- Docker build patch to install this repo inside openedx image:
  - `openedx-dockerfile-post-python-requirements` -> `RUN pip install /openedx/plugins/userops`
- LMS settings patch:
  - `INSTALLED_APPS += ["userops"]`
- LMS URL patch:
  - `path("api/userops/v1/", include("userops.urls"))`

## Verification

Check app installation:

```bash
tutor local run lms ./manage.py lms shell -c "import userops; print('ok')"
```

Check endpoint availability (as staff-authenticated session):

```bash
curl -X POST 'http://localhost:8000/api/userops/v1/users/preview' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: edx-jwt-cookie=...' \
  -d '{"filters": {"cluster": "NORTH 1"}, "limit": 10}'
```

## Notes

- Staff-only permissions are enforced on both endpoints.
- This app intentionally reuses Open edX built-in bulk enrollment endpoint logic via `BulkEnrollView`.
