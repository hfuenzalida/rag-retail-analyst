# RAG Retail Analyst — Deployment & Testing Manual

This guide is written for **non-technical users**. It walks you through:

1. Starting the application on your computer or server  
2. Loading **your real business data** (CSV files)  
3. Running tests to confirm everything works  

You do **not** need to write code. Copy and paste the commands exactly as shown.

---

## Words you will see

| Term | Plain meaning |
|------|----------------|
| **Docker** | A program that runs the app in isolated containers (like lightweight virtual machines). |
| **Compose file** | A recipe that tells Docker which services to start (database, API, website). |
| **API** | The backend “brain” that answers questions (runs on port 8000). |
| **Frontend / UI** | The website you click in your browser (port 3000). |
| **CSV** | A spreadsheet file saved as “Comma Separated Values” (`.csv`). |
| **Client ID** | An identifier for your company’s data. Default: `demo-retail`. |
| **Admin** | Role that can upload data. |
| **Manager / Analyst** | Roles that ask questions (different access levels). |

---

## What you need before you start

### Hardware & software

- [ ] A computer running **Windows 10/11**, **macOS**, or **Linux**
- [ ] At least **8 GB RAM** (16 GB recommended)
- [ ] **Docker Desktop** installed and running  
  - Download: https://www.docker.com/products/docker-desktop/  
  - After install, open Docker Desktop and wait until it says **“Engine running”**
- [ ] Your project folder unzipped or cloned, for example:  
  `C:\Users\YourName\Downloads\IA Data Analysis`

### Data files (your real datasets)

Prepare **three CSV files** from your business systems (export from Excel, ERP, POS, etc.):

| File purpose | Save as | Load order |
|--------------|---------|------------|
| Product catalog | `products.csv` | **1st** |
| Inventory / stock levels | `inventory.csv` | **2nd** |
| Sales transactions | `sales.csv` | **3rd** |

> **Important:** Load **products first**, then **inventory**, then **sales**. Sales rows reference product SKUs that must already exist.

### Optional (for nicer answers)

- A local AI server (Ollama) — summaries can be polished automatically  
- If you skip this, the app still works using factual numbers from your data

---

## Part 1 — First deployment (local test environment)

Use this section to run everything on **your own computer** before going live on a server.

### Step 1.1 — Open a terminal

**Windows:** Press `Win + R`, type `powershell`, press Enter.

**Mac:** Open **Terminal** from Applications → Utilities.

### Step 1.2 — Go to the project folder

Replace the path with your actual folder:

```powershell
cd "C:\Users\YourName\Downloads\IA Data Analysis\infra"
```

### Step 1.3 — Create your local settings file

**Windows (PowerShell):**

```powershell
Copy-Item env.example .env.local
```

**Mac / Linux:**

```bash
cp env.example .env.local
```

You do not need to edit this file for a first local test.

### Step 1.4 — Start the application

```powershell
docker compose -f docker-compose.local.yml up --build
```

**What to expect:**

- The first run takes **5–15 minutes** (downloads and builds).
- You will see many lines of text scrolling — this is normal.
- Wait until you see messages indicating the backend and frontend are ready.
- Leave this window **open** while you use the app.

### Step 1.5 — Open the website

In your web browser, go to:

| Page | Address |
|------|---------|
| **Analyst (ask questions)** | http://localhost:3000 |
| **Admin (upload data)** | http://localhost:3000/admin |
| **API health check** | http://localhost:8000/healthz |

On the Analyst page, click **“Check API health”**. You should see:  
`API: ok (local)`

If that works, deployment on your machine succeeded.

### Step 1.6 — Stop the application (when finished)

In the terminal window, press **Ctrl + C**, then run:

```powershell
docker compose -f docker-compose.local.yml down
```

---

## Part 2 — Prepare your real CSV files

Your CSV files must have a **header row** (column names in the first line). The system recognizes common column names automatically.

### Products file (`products.csv`)

**Required columns** (any of these header names work):

| Field | Accepted column names |
|-------|------------------------|
| Product code | `sku`, `ItemCode`, `product_code` |
| Price | `unit_price`, `price`, `retail_price` |

**Optional:** `category`, `brand`, `unit_cost`, `margin_pct`, `status`

**Example:**

```csv
sku,category,unit_price,unit_cost
SHOE-001,Shoes,120.00,55.00
BAG-002,Accessories,80.00,35.00
```

### Inventory file (`inventory.csv`)

**Required columns:**

| Field | Accepted column names |
|-------|------------------------|
| Product code | `sku`, `ItemCode` |
| Location | `location`, `store_id`, `warehouse` |
| Quantity on hand | `on_hand_qty`, `onhand`, `quantity` |

**Example:**

```csv
sku,location,on_hand_qty
SHOE-001,STORE-A,25
SHOE-001,STORE-B,0
BAG-002,STORE-A,10
```

### Sales file (`sales.csv`)

**Required columns:**

| Field | Accepted column names |
|-------|------------------------|
| Sale ID | `sale_id`, `transaction_id`, `order_id` |
| Date | `sale_date`, `SoldDate`, `date` |
| Product code | `sku`, `ItemCode` |
| Quantity | `quantity`, `qty`, `units` |
| Price | `unit_price`, `price` |

**Optional:** `store_id`, `channel`, `net_revenue`, `discount`

**Example:**

```csv
sale_id,sale_date,store_id,sku,quantity,unit_price,net_revenue
S001,2026-05-15,STORE-A,SHOE-001,2,120.00,240.00
S002,2026-05-20,STORE-B,SHOE-001,1,120.00,120.00
```

### Data quality checklist

Before uploading, confirm:

- [ ] Dates use format **YYYY-MM-DD** (example: `2026-05-15`)
- [ ] Numbers do not contain currency symbols (`$`, `€`) — use plain numbers
- [ ] SKUs in sales and inventory **match** SKUs in products
- [ ] No completely empty rows
- [ ] File is saved as **UTF-8 CSV** (standard export from Excel: “CSV UTF-8”)

---

## Part 3 — Load your real data (Admin page)

### Step 3.1 — Open Admin

Go to: **http://localhost:3000/admin**

### Step 3.2 — Upload products first

1. Under **Target table**, select **`products`**
2. Click **Choose file** and select your `products.csv`
3. Click **Propose mapping**
4. Review the mapping table:
   - Each **required** row should show **yes** in the Required column
   - If you see **“Missing required”**, fix your CSV headers and try again
5. Click **Confirm and load data**
6. Wait for the green success message (example: `Loaded 150 rows into products`)

### Step 3.3 — Upload inventory

Repeat Step 3.2 with **`inventory`** selected and your `inventory.csv`.

### Step 3.4 — Upload sales

Repeat Step 3.2 with **`sales`** selected and your `sales.csv`.

> **Note:** The app tags all uploaded rows with client ID **`demo-retail`**. Do not change this unless your IT team has configured a different client ID in production.

---

## Part 4 — Test with real data (Analyst page)

Go to: **http://localhost:3000**

### Step 4.1 — Set filters (recommended)

Use the date filters to match a period you know from your own reports:

- **Start date** and **End date** — pick the month or range you want to test
- Optionally set **Store**, **Category**, or **SKU** if your data uses them

### Step 4.2 — Choose your role

| Role | What to use it for |
|------|-------------------|
| **Manager** | High-level summaries (revenue, stock-out rate) |
| **Analyst** | Deeper analysis (drivers, margin — if data supports it) |
| **Admin** | Same as analyst for testing |

### Step 4.3 — Ask these test questions

Try each question and check that the answer includes **numbers** and **citations**:

| # | Question | What a good answer looks like |
|---|----------|-------------------------------|
| 1 | `What was total net revenue last month?` | A revenue number matching your reports (approx.) |
| 2 | `How many units were sold in May 2026?` | Unit count for your date range |
| 3 | `What is our stock-out rate?` | A percentage; list of out-of-stock SKUs if applicable |
| 4 | `Why did revenue change by category?` | Driver breakdown (use **Analyst** role) |
| 5 | `Which SKUs are out of stock?` | References inventory with zero quantity |

### Step 4.4 — Pass / fail criteria

**PASS** if:

- [ ] Each question returns an answer (not a blank page)
- [ ] Numbers are in the same ballpark as your known reports
- [ ] The answer panel shows **Metrics**, **Citations**, and a **Summary**
- [ ] Sensitive questions (customer names, salaries) are **refused** politely

**FAIL** if:

- Error banner appears — note the exact message (see Troubleshooting)
- Numbers are wildly wrong — check date filters and CSV data
- “No data” — confirm you loaded all three CSV files in order

---

## Part 5 — Automated health checks (optional, with IT help)

If someone on your team can run Python, these scripts confirm the system is healthy:

Open a **new** terminal (leave Docker running in the other one):

```powershell
cd "C:\Users\YourName\Downloads\IA Data Analysis"
python infra/scripts/run_smoke.py
python infra/scripts/lint_config.py
```

**Expected:** messages saying smoke tests and config lint **passed**.

For a full automated test suite (requires Python packages installed):

```powershell
cd backend
pip install -r requirements.txt
pytest app/tests -q --ignore=app/tests/test_integration_db.py --ignore=app/tests/test_integration_query.py --ignore=app/tests/test_integration_rag.py
```

**Expected:** a line ending with `passed` and **zero failed**.

---

## Part 6 — Production deployment (live server)

Only proceed here after **Part 1–4** work correctly with your real CSV data on your computer.

### Step 6.1 — Server requirements

- [ ] A server or VPS with Docker installed
- [ ] A domain name (example: `analytics.yourcompany.com`)
- [ ] HTTPS certificate (usually via your hosting provider or Cloudflare)
- [ ] Strong passwords ready (database + JWT secret)

### Step 6.2 — Create production settings

On the server, in the `infra` folder:

```powershell
Copy-Item env.production.example .env.production
```

Edit `.env.production` and change **at minimum**:

| Setting | What to put |
|---------|-------------|
| `POSTGRES_PASSWORD` | A long random password (20+ characters) |
| `APP_AUTH_JWT_SECRET` | Another long random string (32+ characters) |
| `APP_BASE_URL` | Your public website URL |
| `NEXT_PUBLIC_API_URL` | Your public API URL |
| `APP_PILOT_CLIENT_ID` | `demo-retail` (or your configured client ID) |

> **Never** share or email these passwords. Store them in a password manager.

### Step 6.3 — Start production stack

```powershell
cd infra

# One-time database setup with demo data (SKIP if using only your real CSVs):
# docker compose -f docker-compose.production.yml --profile init up seed-demo

# Start live services:
docker compose -f docker-compose.production.yml up --build -d
```

### Step 6.4 — Verify production is ready

```powershell
curl http://localhost:8000/healthz
curl http://localhost:8000/healthz/ready
```

Both should return JSON with `"status": "ok"` or `"status": "ready"`.

### Step 6.5 — Load real data on production

Same as Part 3, but use your **production URL** instead of `localhost`:

`https://your-domain.com/admin`

### Step 6.6 — Before inviting users

- [ ] Real data loaded and tested (Part 4 questions)
- [ ] Smoke script passed
- [ ] Passwords rotated from example values
- [ ] HTTPS working in the browser (padlock icon)
- [ ] IT has reviewed `infra/flags/runtime-controls.yaml` (feature flags)

---

## Part 7 — Troubleshooting

| Problem | Likely cause | What to do |
|---------|--------------|------------|
| Docker says “cannot connect” | Docker Desktop not running | Open Docker Desktop; wait for “Engine running” |
| `localhost:3000` does not load | Services still starting | Wait 2–3 minutes; check terminal for errors |
| “Missing required fields” on upload | CSV column names not recognized | Rename headers to examples in Part 2 |
| Revenue number seems wrong | Wrong date filter | Set start/end dates to match your CSV dates |
| “Admin role required” | Ingest blocked | Confirm `APP_ENABLE_INGEST=true` in env file |
| “Client not authorized” (production) | Wrong client ID | Use `demo-retail` or ask IT to update tenant config |
| Upload works but queries empty | Sales loaded before products | Re-load in order: products → inventory → sales |
| Port already in use | Another app on 3000/8000 | Stop other apps or change ports in env file |

### Getting help from IT

When asking for help, provide:

1. Which step you were on  
2. The **exact error message** (screenshot helps)  
3. Whether you are on **local** or **production**  
4. Which CSV file you were uploading (products / inventory / sales)

---

## Part 8 — Security reminders

- Do **not** put real customer names, emails, or salaries in test questions — the system is designed to refuse PII.
- Do **not** commit `.env.production` or `.env.local` to email or public folders.
- Rotate passwords after first setup.
- In production, restrict Admin page access to trusted staff only (ask IT to add login / VPN).
- Keep Docker and the host operating system updated.

---

## Quick reference card

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL DEPLOY                                               │
│  cd infra                                                   │
│  Copy-Item env.example .env.local                           │
│  docker compose -f docker-compose.local.yml up --build      │
│                                                             │
│  OPEN IN BROWSER                                            │
│  Analyst:  http://localhost:3000                            │
│  Admin:    http://localhost:3000/admin                      │
│  Health:   http://localhost:8000/healthz                    │
│                                                             │
│  LOAD DATA (Admin page, in order)                           │
│  1. products.csv  →  2. inventory.csv  →  3. sales.csv   │
│                                                             │
│  TEST QUESTION                                              │
│  "What was total net revenue last month?"                   │
│  (set date filters to match your data)                      │
│                                                             │
│  STOP                                                       │
│  Ctrl+C  then  docker compose -f docker-compose.local.yml down │
└─────────────────────────────────────────────────────────────┘
```

---

## Document history

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-06-30 | Initial manual for local + production deploy with real CSV datasets |

For technical details, see `memory-bank/core/` and `infra/` in the project folder.
