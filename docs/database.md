# Database

MongoDB collections, accessed via Beanie ODM. All timestamps are stored as UTC `datetime`. Document field names are snake_case in Python; the JSON wire format is camelCase via Pydantic schema aliases.

## `users`

Identity and role for everyone who can log in.

| Field | Type | Notes |
| --- | --- | --- |
| `_id` | ObjectId | Beanie primary key |
| `email` | string | lowercase, validated |
| `password_hash` | string | bcrypt hash, never exposed |
| `full_name` | string | display name |
| `role` | enum `user` \| `admin` | drives authorization |
| `created_at`, `updated_at` | datetime | UTC |

Indexes: unique on `email` (`users_email_unique`).

## `animals`

Every animal currently in the shelter or already adopted.

| Field | Type | Notes |
| --- | --- | --- |
| `_id` | ObjectId | |
| `name` | string | display name |
| `species` | enum `dog` \| `cat` \| `bird` \| `rabbit` \| `other` | |
| `breed` | string \| null | optional |
| `age_years` | float | half-years allowed |
| `gender` | enum `male` \| `female` | |
| `vaccinated`, `neutered` | bool | |
| `status` | enum `available` \| `pending` \| `adopted` | adoption lifecycle |
| `description` | string | public-facing copy |
| `photos` | list[string] | each entry is the URL `/images/{id}` |
| `arrived_at` | datetime | intake date |
| `created_at`, `updated_at` | datetime | |

Indexes: text on (`name`, `breed`, `description`) for the `q` filter; compound on (`status`, `species`) for the listing query.

## `animal_notes`

Public health/care notes added by admins; readable by anyone.

| Field | Type | Notes |
| --- | --- | --- |
| `_id` | ObjectId | |
| `animal_id` | ObjectId | refs `animals` |
| `text` | string | |
| `author_id` | ObjectId | refs `users` (admin) |
| `created_at` | datetime | |

Indexes: single field on `animal_id`.

## `animal_images`

Raw image bytes for animals, streamed back through `/images/{id}`.

| Field | Type | Notes |
| --- | --- | --- |
| `_id` | ObjectId | |
| `animal_id` | ObjectId | refs `animals` |
| `content_type` | string | `image/jpeg`, `image/png`, or `image/webp` |
| `data` | binary | bytes, max 1 MB |
| `uploaded_at` | datetime | |

Indexes: single field on `animal_id`.

## `adoption_requests`

User-submitted requests, plus post-adoption updates once approved.

| Field | Type | Notes |
| --- | --- | --- |
| `_id` | ObjectId | |
| `animal_id` | ObjectId | refs `animals` |
| `user_id` | ObjectId | refs `users` (applicant) |
| `message` | string \| null | optional cover note |
| `status` | enum `pending` \| `approved` \| `rejected` \| `completed` | |
| `decided_by_id` | ObjectId \| null | admin who decided |
| `decided_at` | datetime \| null | decision timestamp |
| `updates` | list[embedded] | each `{text, photo_url, created_at}` |
| `created_at`, `updated_at` | datetime | |

Indexes: compound on (`user_id`, `status`) for "my adoptions"; compound on (`status`, `created_at`) for the admin queue.

## `favorites`

Per-user shortlists of animals.

| Field | Type | Notes |
| --- | --- | --- |
| `_id` | ObjectId | |
| `user_id` | ObjectId | refs `users` |
| `animal_id` | ObjectId | refs `animals` |
| `created_at` | datetime | |

Indexes: unique compound on (`user_id`, `animal_id`) — guarantees idempotent favoriting.
