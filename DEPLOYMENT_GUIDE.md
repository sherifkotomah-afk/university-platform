# Deployment Guide — Dashboards Only, No Terminal

This guide deploys the whole platform using only the web dashboards for
Supabase, Render, and Vercel. You will not open a terminal at any point.
Database migrations run automatically as part of Render's deploy process,
and your first admin account is created through your browser using the
API's built-in interactive docs page — not a script.

You will need: a GitHub account (to hold the code so Render/Vercel can
deploy it), and accounts on Supabase, Render, Vercel, and Paystack.

---

## Step 1 — Put the code on GitHub (still no terminal)

1. Go to [github.com/new](https://github.com/new) and create a new empty
   repository (e.g. `university-platform`). Keep it **Private** if this is
   for a specific institution's real data.
2. On the new repo's page, click **"uploading an existing file"**.
3. Unzip the project I gave you on your computer (just double-click the
   zip file — Windows/Mac both do this natively, no terminal).
4. Drag the whole `university-platform` folder's contents into GitHub's
   upload box, then click **Commit changes**.

You now have the code on GitHub without ever opening a terminal.

---

## Step 2 — Supabase (Database)

1. Go to [supabase.com](https://supabase.com) → **New Project**.
2. Pick a name, a strong database password (save it somewhere), and a
   region close to Ghana (e.g. an EU region).
3. Once it finishes provisioning (~2 minutes), go to
   **Project Settings (gear icon) → Database**.
4. Scroll to **Connection string**, select the **URI** tab, and switch the
   mode dropdown to **Session pooler** (important — not "Transaction
   pooler"). Copy that string. It looks like:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-region.pooler.supabase.com:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` in that string with the database password you
   set in step 2. Save this full string somewhere — you'll paste it into
   Render in the next step, as `DATABASE_URL`.

That's it for Supabase — you don't create any tables by hand here; Render
will do that automatically on first deploy.

---

## Step 3 — Render (Backend)

1. Go to [render.com](https://render.com) → **New +** → **Blueprint**.
2. Connect your GitHub account if prompted, then select the
   `university-platform` repo you created.
3. Render will detect `backend/render.yaml` automatically and show you the
   service it's about to create. Click **Apply**.
4. It will ask you to fill in the environment variables marked
   `sync: false` — these are boxes in Render's UI, just click and type:

   | Variable | What to put |
   |---|---|
   | `DATABASE_URL` | The Supabase connection string from Step 2 |
   | `JWT_SECRET_KEY` | Any long random string — see the box below for a way to generate one without a terminal |
   | `ALLOWED_ORIGINS` | Leave as `http://localhost:3000` for now — you'll come back and update this after Step 4 |
   | `PAYSTACK_SECRET_KEY` | From Step 5 below (you can leave blank for now and fill in later) |
   | `PAYSTACK_PUBLIC_KEY` | Same as above |
   | `SETUP_SECRET_KEY` | Another long random string, different from JWT_SECRET_KEY |

   > **Generating a random secret without a terminal:** go to
   > [1password.com/password-generator](https://1password.com/password-generator/)
   > or any password generator website, set length to 50+, uncheck
   > "symbols" if you want to keep it simple, and copy the result. Do this
   > twice — once for `JWT_SECRET_KEY`, once for `SETUP_SECRET_KEY`.

5. Click **Deploy**. Render will now: install everything, run the database
   migration (creating all 44 tables in your Supabase database
   automatically), and start the server. Watch the **Logs** tab — when you
   see `Application startup complete`, it's live.
6. Your backend's URL is shown at the top of the Render page, looking like
   `https://university-platform-api.onrender.com`. Copy it.
7. Test it: open `https://your-url.onrender.com/health` in your browser —
   you should see `{"status":"ok"}`. If you see an error instead, check the
   **Logs** tab on Render for the reason (most common cause: a typo in
   `DATABASE_URL`).

---

## Step 4 — Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**.
2. Import the same `university-platform` GitHub repo.
3. Vercel will ask for a **Root Directory** — click **Edit** next to it and
   select `frontend`.
4. Under **Environment Variables**, add:
   | Name | Value |
   |---|---|
   | `VITE_API_URL` | Your Render URL from Step 3 (e.g. `https://university-platform-api.onrender.com`) |
5. Click **Deploy**.
6. Once done, Vercel gives you a URL like `https://university-platform.vercel.app`.
   Open it — you should see the public homepage.

---

## Step 5 — Connect the frontend and backend properly

Right now the backend only trusts requests from `localhost`. Fix that:

1. Go back to your **Render** service → **Environment** tab.
2. Edit `ALLOWED_ORIGINS` to your real Vercel URL from Step 4, e.g.:
   ```
   https://university-platform.vercel.app
   ```
   (You can list more than one, comma-separated, if you also want to keep
   `http://localhost:3000` for later local testing.)
3. Click **Save Changes** — Render redeploys automatically.

---

## Step 6 — Paystack (Payments)

1. Go to [paystack.com](https://paystack.com) → create an account.
2. Once logged in, go to **Settings → API Keys & Webhooks**.
3. Copy the **Test Secret Key** and **Test Public Key** shown there (live
   keys require Paystack to verify your business first — use test keys
   until then, they work identically for development).
4. Go back to **Render → Environment**, paste these into
   `PAYSTACK_SECRET_KEY` and `PAYSTACK_PUBLIC_KEY`, save.

---

## Step 7 — Create your first admin account (via browser, not a terminal)

1. Open `https://your-render-url.onrender.com/docs` in your browser. This
   is an interactive page FastAPI generates automatically — you click
   buttons and fill in boxes, nothing is typed into a command line.
2. Scroll to **POST /setup/bootstrap**, click it to expand, then click
   **"Try it out"**.
3. In the box that appears, fill in the JSON with your real details:
   ```json
   {
     "setup_secret": "the SETUP_SECRET_KEY you set in Render",
     "institution_name": "Your University Name",
     "short_code": "YUN",
     "grading_system": "GPA",
     "academic_year": "2026/2027",
     "admin_email": "you@yourdomain.com",
     "admin_password": "a-strong-password",
     "admin_first_name": "Your",
     "admin_last_name": "Name"
   }
   ```
4. Click **Execute**. A green `201` response means it worked.
5. Go to your Vercel site, click **Login**, and log in with the email and
   password you just set. You'll be asked to change your password on
   first login — that's expected.

You now have a working admin account and can use the Admin dashboard on
the site itself for everything else (adding schools/programmes/courses,
setting up fee items, creating faculty accounts) — no more need for
`/docs` after this point.

---

## What "no terminal" means here, precisely

- You never install anything on your own computer.
- You never type a command into a black command-line window.
- Database tables are created automatically by Render during deploy.
- Your first admin account is created by filling in a form on a web page
  (`/docs`), which is a browser interface, not a terminal.
- All ongoing work (adding programmes, approving grades, managing fees)
  happens through the actual website UI once you're logged in as admin.

The one thing that still technically runs "a command" is Render itself
executing `alembic upgrade head` — but that happens automatically on
Render's servers as part of clicking "Deploy". You never see or type that
command yourself.

---

## If something goes wrong

- **Render shows the backend crashed on deploy** → check the **Logs** tab.
  The most common cause is `DATABASE_URL` being pasted with a typo, or
  forgetting to replace `[YOUR-PASSWORD]` in the Supabase connection string.
- **The website loads but shows errors talking to the API** → check
  `ALLOWED_ORIGINS` on Render matches your exact Vercel URL (including
  `https://`, no trailing slash).
- **`/setup/bootstrap` says "already been completed"** → this is expected
  if you already created an admin. Log in normally instead. If you truly
  need to reset, you'd need to clear the `users` table in Supabase's
  Table Editor (a UI, not a terminal) and try again.
