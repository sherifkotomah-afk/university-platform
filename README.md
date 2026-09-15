# University Platform

A full university web platform: public website, applicant portal, student portal,
faculty portal, and admin/registrar back office. Built for Ghanaian tertiary
institution structure (WASSCE admissions, GTEC-regulated itemized fees, GPA/CWA
grading) and designed to be **white-labeled** — rebrand it for a different
institution by editing one config file plus one database table, no code changes.

- **Frontend:** React (Vite) — deploy on **Vercel**
- **Backend:** Python (FastAPI) — deploy on **Render**
- **Database:** PostgreSQL — hosted on **Supabase**
- **Payments:** **Paystack** (Ghana Cedis)

---

## 1. Project Structure

```
university-platform/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py          # App entrypoint, router registration
│   │   ├── config.py        # Environment-variable settings
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── models/          # SQLAlchemy models (one file per domain)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API endpoints (one file per domain)
│   │   └── core/            # security, deps, paystack client, grading engine
│   ├── alembic/              # Database migrations
│   ├── schema.sql            # Reference: full schema as raw SQL
│   ├── requirements.txt
│   ├── render.yaml           # Render deployment blueprint
│   └── .env.example
└── frontend/                 # React application
    ├── src/
    │   ├── pages/            # public/, auth/, applicant/, student/, faculty/, admin/
    │   ├── components/       # Navbar, PortalLayout, ProtectedRoute
    │   ├── context/          # AuthContext (login state, tokens)
    │   ├── api/              # Axios client with auto token refresh
    │   └── config/brand.js   # ⭐ WHITE-LABEL CONFIG — edit this to rebrand
    ├── vercel.json
    └── .env.example
```

---

## 2. Set Up Supabase (Database)

1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings → Database → Connection string → URI**.
   Use the **Session pooler** connection string (not "Transaction pooler") —
   this matters for SQLAlchemy's connection handling with Render.
3. Copy that connection string; you'll use it as `DATABASE_URL`.
4. Note: Supabase's own dashboard/auth features are **not** used here — we
   connect directly to the Postgres database with our own FastAPI backend
   and our own auth system (JWT). Supabase is being used purely as managed
   Postgres hosting.

### Run the migrations

From your local machine (with the repo cloned):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: paste your Supabase DATABASE_URL, generate a JWT_SECRET_KEY:
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

This creates all 44 tables in your Supabase database. You can verify in the
Supabase dashboard under **Table Editor**.

### Seed initial data

You need at least one row in `institution_settings` and one admin user before
the platform is usable. Run this Python snippet once (adjust values):

```python
# seed.py — run with: python3 seed.py
from app.database import SessionLocal
from app.models.core import InstitutionSettings, User
from app.core.security import hash_password

db = SessionLocal()

db.add(InstitutionSettings(
    institution_name="Sample University",
    short_code="SU",
    grading_system="GPA",       # or "CWA"
    academic_year="2026/2027",
    current_semester=1,
))

db.add(User(
    email="admin@sampleuniversity.edu.gh",
    password_hash=hash_password("ChangeThisPassword123!"),
    role="admin",
    first_name="System",
    last_name="Admin",
    must_change_password=True,
))

db.commit()
print("Seed complete. Log in as admin@sampleuniversity.edu.gh and change the password immediately.")
```

---

## 3. Set Up Render (Backend)

1. Push this repo to GitHub.
2. On [render.com](https://render.com): **New → Blueprint**, point it at your
   repo. It will read `backend/render.yaml` automatically. Alternatively,
   create a **Web Service** manually with:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Under **Environment**, set:
   - `DATABASE_URL` — your Supabase connection string
   - `JWT_SECRET_KEY` — the secret you generated earlier
   - `ALLOWED_ORIGINS` — your Vercel URL, e.g. `https://your-app.vercel.app`
     (add `http://localhost:3000` too while developing)
   - `PAYSTACK_SECRET_KEY` / `PAYSTACK_PUBLIC_KEY` — see section 5
   - `ENVIRONMENT` — `production`
4. Deploy. Check `https://your-service.onrender.com/health` returns
   `{"status": "ok"}`.
5. Full interactive API docs are auto-generated at
   `https://your-service.onrender.com/docs`.

**Note on Render's free tier:** free services spin down after inactivity and
take ~30–60 seconds to wake on the next request. This is fine for demos but
worth knowing — students hitting a "slow first load" isn't a bug.

---

## 4. Set Up Vercel (Frontend)

1. On [vercel.com](https://vercel.com): **New Project**, import the same repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite**.
4. Under **Environment Variables**, add:
   - `VITE_API_URL` = your Render backend URL (e.g. `https://university-platform-api.onrender.com`)
5. Deploy.
6. Go back to Render and add this Vercel URL to `ALLOWED_ORIGINS`, then
   redeploy the backend (CORS will block requests otherwise).

---

## 5. Set Up Paystack (Payments)

1. Create an account at [paystack.com](https://paystack.com).
2. Go to **Settings → API Keys & Webhooks**. You'll see test keys immediately;
   live keys require Paystack to approve your business (KYC) — use test keys
   until then.
3. Copy `PAYSTACK_SECRET_KEY` and `PAYSTACK_PUBLIC_KEY` into Render's
   environment variables (never put the secret key in frontend code).
4. Test the flow: as a student, go to **Fees & Payments**, click "Make a
   Payment" — this calls `/fees/payments/initiate`, which asks Paystack to
   create a transaction, then redirects to Paystack's checkout page.
5. After payment, Paystack redirects back to your app with `?reference=...`
   in the URL. The frontend automatically calls `/fees/payments/verify`,
   which asks Paystack directly whether the payment really succeeded before
   marking anything as paid — **never trust the redirect alone**, this is
   why verification is server-to-server.
6. For production, also consider setting up a Paystack **webhook** pointed at
   a new backend endpoint as a backup confirmation path, in case a student
   closes the browser tab before the redirect completes. **This is now
   built** — see `POST /fees/payments/webhook`. Configure it in Paystack
   Dashboard → Settings → API Keys & Webhooks → Webhook URL:
   `https://your-render-url.onrender.com/fees/payments/webhook`. Paystack
   signs every webhook call, and the backend verifies that signature before
   trusting anything in it — this is checked automatically, nothing for you
   to configure beyond pasting the URL.

---

## 6. White-Labeling for a Different Institution

To repackage this platform for a different university/investor pitch:

1. **Branding:** edit `frontend/src/config/brand.js` — name, colors, logo,
   contact info. Redeploy the frontend.
2. **Academic structure:** edit the `institution_settings` row in the
   database (grading system: GPA or CWA; current academic year/semester).
   No redeploy needed — the backend reads this live.
3. **Fee/levy list:** use the admin dashboard (or `POST /fees/items`) to set
   up that institution's specific levies and amounts — these are meant to
   change yearly per GTEC approval, so nothing is hardcoded.
4. **Academic catalog:** schools, departments, programmes, and courses are
   all just database rows — seed a new institution's catalog via the admin
   endpoints or directly in Supabase's Table Editor.

---

## 7. What's Built vs. What Needs Attention Before Real Students Use It

**Built and working:**
- Full academic structure, admissions (WASSCE/GTEC fields), course
  registration, results with GPA/CWA calculation, itemized fees with
  Paystack payments (including a signature-verified webhook as a backup
  confirmation path), faculty gradebook with registrar approval workflow,
  admin back office, content management, messaging, support tickets,
  hostels, library, clubs, **real file uploads** (applicants and faculty
  upload actual files, not just paste a URL), a themed light/dark UI, and
  per-tab independent login sessions.

**Needs attention before production use with real student data:**
- **Legal/compliance review** — this handles personal and financial data;
  have someone review against Ghana's Data Protection Act requirements.
- **File storage durability** — uploads currently save to local disk on the
  Render instance. This works today, but Render's disk is **not persistent
  across deploys/restarts** — a redeploy can wipe uploaded files. Before
  real students upload real documents long-term, swap the storage backend
  in `app/routers/uploads.py` for Supabase Storage or S3. The upload
  endpoint's shape (accepts a file, returns a URL) won't need to change on
  the frontend side when you do this.
- **Email/SMS notifications** — the `notifications` table exists but nothing
  currently sends real emails/SMS (e.g. via SendGrid, Twilio, or a Ghanaian
  SMS gateway). Currently notifications are in-app only.
- **Paystack webhook** — see section 5, point 6.
- **Rate limiting / abuse protection** on public endpoints (registration,
  login).
- **Automated backups** — Supabase has this, confirm your plan includes the
  retention window you need.
- **Load testing** — before a real registration period rush.

---

## 8. Local Development

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
# API at http://localhost:8000, docs at http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# App at http://localhost:3000
```

---

## 9. Default Roles

| Role | Created via | Notes |
|---|---|---|
| `applicant` | Public `/register` page | Self-service sign-up |
| `student` | Automatic, when admin sets an application to "Enrolled" | Never self-service |
| `faculty` | Admin back office (`POST /admin/users`, then `/admin/faculty-profiles`) | |
| `admin` / `registrar` / `finance` | Admin back office, or the seed script for the very first admin | |

First login for any admin-created account requires a password change
(`must_change_password` flag).
