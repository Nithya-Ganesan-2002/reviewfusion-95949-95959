# Supabase Integration Guide for review_radar_backend

## Overview
This backend will connect to Supabase for authentication and persistent storage of users and product reviews.

## Required Environment Variables
Set the following variables, which are already provided in your environment and `.env` for local dev:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Project-level API key (service role for backend)
- `SUPABASE_DB_URL`: Database connection string (if direct SQL-level access is needed)
- `SECRET_KEY`: JWT secret for signing access tokens (define securely for prod)

Example `.env` section:
```
SUPABASE_URL=https://ypcnivwbltjucfzxbcoi.supabase.co
SUPABASE_KEY=YOUR_BACKEND_SERVICE_ROLE_KEY
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.ypcnivwbltjucfzxbcoi.supabase.co:5432/postgres
SECRET_KEY=super-secret-development-key
```

## Usage
- All database reads/writes should use the official Supabase Python client where possible.
- Authentication (register/login) should write user details to Supabase's auth table or a custom users table.
- Reviews should be stored in a table named `reviews` with `product_id`, `user_id`, `rating`, `title`, `content`,`timestamp`.

## Structure
- The backend *currently* only stubs out the Supabase client. Replace with a real client (e.g. [supabase-py](https://github.com/supabase-community/supabase-py)) and implement the methods according to your data model.
- Review AI summaries do NOT go in Supabase unless you want to cache them.

## Security
- Never expose your `SUPABASE_KEY` in frontend apps.
- Limit read/write permissions server-side using RLS and server-side keys only.

## Testing
- Use test data in a non-production Supabase project.
