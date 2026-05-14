
import os
import json
import git
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
REPO_URL = "https://github.com/PhonePe/pulse.git"
CLONE_DIR = "phonepe_pulse_data"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",   
    "database": "phonepe",
}

STATE_NAME_MAP = {
    "andaman-&-nicobar-islands": "Andaman & Nicobar Island",
    "andhra-pradesh": "Andhra Pradesh",
    "arunachal-pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh",
    "dadra-&-nagar-haveli-&-daman-&-diu": "Dadra and Nagar Haveli and Daman and Diu",
    "delhi": "NCT of Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal-pradesh": "Himachal Pradesh",
    "jammu-&-kashmir": "Jammu & Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya-pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "puducherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil-nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar-pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west-bengal": "West Bengal",
}


def fmt_state(raw: str) -> str:
    """Convert a folder-style state name to its clean display name."""
    return STATE_NAME_MAP.get(raw, raw.replace("-", " ").title())



# STEP 1  —  CLONE REPOSITORY

def clone_repo():
    if os.path.exists(CLONE_DIR):
        print(f"[✓] Repository already present at ./{CLONE_DIR}")
        return
    print("[…] Cloning PhonePe Pulse repository (≈ 200 MB) …")
    git.Repo.clone_from(REPO_URL, CLONE_DIR)
    print("[✓] Clone complete.")



# STEP 2  —  EXTRACT & TRANSFORM


# ── helpers ──
def _read_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def _walk_state_year_quarter(base_path):
    """Yield (state, year, quarter, data_dict) for every JSON under base_path/state/."""
    state_root = os.path.join(base_path, "state")
    if not os.path.isdir(state_root):
        return
    for state_folder in sorted(os.listdir(state_root)):
        sp = os.path.join(state_root, state_folder)
        if not os.path.isdir(sp):
            continue
        for year_folder in sorted(os.listdir(sp)):
            yp = os.path.join(sp, year_folder)
            if not os.path.isdir(yp):
                continue
            for fname in sorted(os.listdir(yp)):
                if not fname.endswith(".json"):
                    continue
                quarter = int(fname.replace(".json", ""))
                data = _read_json(os.path.join(yp, fname))
                yield state_folder, int(year_folder), quarter, data


# ── 2-A  Aggregated Transaction ──
def extract_aggregated_transaction():
    base = os.path.join(CLONE_DIR, "data", "aggregated", "transaction", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        td = (raw.get("data") or {}).get("transactionData") or []
        for item in td:
            for pi in item.get("paymentInstruments", []):
                rows.append({
                    "state": fmt_state(state),
                    "year": year,
                    "quarter": qtr,
                    "transaction_type": item["name"],
                    "transaction_count": pi["count"],
                    "transaction_amount": pi["amount"],
                })
    df = pd.DataFrame(rows)
    print(f"  aggregated_transaction  → {len(df):>8,} rows")
    return df


# ── 2-B  Aggregated User ──
def extract_aggregated_user():
    base = os.path.join(CLONE_DIR, "data", "aggregated", "user", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        d = raw.get("data") or {}
        agg = d.get("aggregated") or {}
        registered = agg.get("registeredUsers", 0)
        app_opens = agg.get("appOpens", 0)
        devices = d.get("usersByDevice") or []
        if devices:
            for dev in devices:
                rows.append({
                    "state": fmt_state(state),
                    "year": year,
                    "quarter": qtr,
                    "brand": dev.get("brand", "Unknown"),
                    "user_count": dev.get("count", 0),
                    "user_percentage": dev.get("percentage", 0),
                    "registered_users": registered,
                    "app_opens": app_opens,
                })
        else:
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "brand": None,
                "user_count": 0,
                "user_percentage": 0,
                "registered_users": registered,
                "app_opens": app_opens,
            })
    df = pd.DataFrame(rows)
    print(f"  aggregated_user         → {len(df):>8,} rows")
    return df


# ── 2-C  Aggregated Insurance ──
def extract_aggregated_insurance():
    base = os.path.join(CLONE_DIR, "data", "aggregated", "insurance", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        td = (raw.get("data") or {}).get("transactionData") or []
        for item in td:
            for pi in item.get("paymentInstruments", []):
                rows.append({
                    "state": fmt_state(state),
                    "year": year,
                    "quarter": qtr,
                    "transaction_type": item["name"],
                    "transaction_count": pi["count"],
                    "transaction_amount": pi["amount"],
                })
    df = pd.DataFrame(rows)
    print(f"  aggregated_insurance    → {len(df):>8,} rows")
    return df


# ── 2-D  Map Transaction ──
def extract_map_transaction():
    base = os.path.join(CLONE_DIR, "data", "map", "transaction", "hover", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        hlist = (raw.get("data") or {}).get("hoverDataList") or []
        for h in hlist:
            for m in h.get("metric", []):
                rows.append({
                    "state": fmt_state(state),
                    "year": year,
                    "quarter": qtr,
                    "district": h["name"].title(),
                    "transaction_count": m["count"],
                    "transaction_amount": m["amount"],
                })
    df = pd.DataFrame(rows)
    print(f"  map_transaction         → {len(df):>8,} rows")
    return df


# ── 2-E  Map User ──
def extract_map_user():
    base = os.path.join(CLONE_DIR, "data", "map", "user", "hover", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        hdata = (raw.get("data") or {}).get("hoverData") or {}
        for district, vals in hdata.items():
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "district": district.title(),
                "registered_users": vals.get("registeredUsers", 0),
                "app_opens": vals.get("appOpens", 0),
            })
    df = pd.DataFrame(rows)
    print(f"  map_user                → {len(df):>8,} rows")
    return df


# ── 2-F  Map Insurance ──
def extract_map_insurance():
    base = os.path.join(CLONE_DIR, "data", "map", "insurance", "hover", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        hlist = (raw.get("data") or {}).get("hoverDataList") or []
        for h in hlist:
            for m in h.get("metric", []):
                rows.append({
                    "state": fmt_state(state),
                    "year": year,
                    "quarter": qtr,
                    "district": h["name"].title(),
                    "transaction_count": m["count"],
                    "transaction_amount": m["amount"],
                })
    df = pd.DataFrame(rows)
    print(f"  map_insurance           → {len(df):>8,} rows")
    return df


# ── 2-G  Top Transaction ──
def extract_top_transaction():
    base = os.path.join(CLONE_DIR, "data", "top", "transaction", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        d = raw.get("data") or {}
        for district in d.get("districts", []):
            met = district.get("metric", {})
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "entity_name": district["entityName"].title(),
                "entity_type": "district",
                "transaction_count": met.get("count", 0),
                "transaction_amount": met.get("amount", 0),
            })
        for pincode in d.get("pincodes", []):
            met = pincode.get("metric", {})
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "entity_name": str(pincode["entityName"]),
                "entity_type": "pincode",
                "transaction_count": met.get("count", 0),
                "transaction_amount": met.get("amount", 0),
            })
    df = pd.DataFrame(rows)
    print(f"  top_transaction         → {len(df):>8,} rows")
    return df


# ── 2-H  Top User ──
def extract_top_user():
    base = os.path.join(CLONE_DIR, "data", "top", "user", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        d = raw.get("data") or {}
        for district in d.get("districts", []):
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "entity_name": district["name"].title(),
                "entity_type": "district",
                "registered_users": district.get("registeredUsers", 0),
            })
        for pincode in d.get("pincodes", []):
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "entity_name": str(pincode["name"]),
                "entity_type": "pincode",
                "registered_users": pincode.get("registeredUsers", 0),
            })
    df = pd.DataFrame(rows)
    print(f"  top_user                → {len(df):>8,} rows")
    return df


# ── 2-I  Top Insurance ──
def extract_top_insurance():
    base = os.path.join(CLONE_DIR, "data", "top", "insurance", "country", "india")
    rows = []
    for state, year, qtr, raw in _walk_state_year_quarter(base):
        d = raw.get("data") or {}
        for district in d.get("districts", []):
            met = district.get("metric", {})
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "entity_name": district["entityName"].title(),
                "entity_type": "district",
                "transaction_count": met.get("count", 0),
                "transaction_amount": met.get("amount", 0),
            })
        for pincode in d.get("pincodes", []):
            met = pincode.get("metric", {})
            rows.append({
                "state": fmt_state(state),
                "year": year,
                "quarter": qtr,
                "entity_name": str(pincode["entityName"]),
                "entity_type": "pincode",
                "transaction_count": met.get("count", 0),
                "transaction_amount": met.get("amount", 0),
            })
    df = pd.DataFrame(rows)
    print(f"  top_insurance           → {len(df):>8,} rows")
    return df



# STEP 3  —  LOAD INTO MYSQL

CREATE_TABLE_SQL = {
    "aggregated_transaction": """
        CREATE TABLE IF NOT EXISTS aggregated_transaction (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            transaction_type VARCHAR(100),
            transaction_count BIGINT,
            transaction_amount DOUBLE
        );
    """,
    "aggregated_user": """
        CREATE TABLE IF NOT EXISTS aggregated_user (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            brand           VARCHAR(50),
            user_count      BIGINT,
            user_percentage DOUBLE,
            registered_users BIGINT,
            app_opens       BIGINT
        );
    """,
    "aggregated_insurance": """
        CREATE TABLE IF NOT EXISTS aggregated_insurance (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            transaction_type VARCHAR(100),
            transaction_count BIGINT,
            transaction_amount DOUBLE
        );
    """,
    "map_transaction": """
        CREATE TABLE IF NOT EXISTS map_transaction (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            district        VARCHAR(100),
            transaction_count BIGINT,
            transaction_amount DOUBLE
        );
    """,
    "map_user": """
        CREATE TABLE IF NOT EXISTS map_user (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            district        VARCHAR(100),
            registered_users BIGINT,
            app_opens       BIGINT
        );
    """,
    "map_insurance": """
        CREATE TABLE IF NOT EXISTS map_insurance (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            district        VARCHAR(100),
            transaction_count BIGINT,
            transaction_amount DOUBLE
        );
    """,
    "top_transaction": """
        CREATE TABLE IF NOT EXISTS top_transaction (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            entity_name     VARCHAR(100),
            entity_type     VARCHAR(20),
            transaction_count BIGINT,
            transaction_amount DOUBLE
        );
    """,
    "top_user": """
        CREATE TABLE IF NOT EXISTS top_user (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            entity_name     VARCHAR(100),
            entity_type     VARCHAR(20),
            registered_users BIGINT
        );
    """,
    "top_insurance": """
        CREATE TABLE IF NOT EXISTS top_insurance (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            state           VARCHAR(100),
            year            INT,
            quarter         INT,
            entity_name     VARCHAR(100),
            entity_type     VARCHAR(20),
            transaction_count BIGINT,
            transaction_amount DOUBLE
        );
    """,
}

INSERT_SQL = {
    "aggregated_transaction": """
        INSERT INTO aggregated_transaction
            (state, year, quarter, transaction_type, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    "aggregated_user": """
        INSERT INTO aggregated_user
            (state, year, quarter, brand, user_count, user_percentage, registered_users, app_opens)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,
    "aggregated_insurance": """
        INSERT INTO aggregated_insurance
            (state, year, quarter, transaction_type, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    "map_transaction": """
        INSERT INTO map_transaction
            (state, year, quarter, district, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    "map_user": """
        INSERT INTO map_user
            (state, year, quarter, district, registered_users, app_opens)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    "map_insurance": """
        INSERT INTO map_insurance
            (state, year, quarter, district, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    "top_transaction": """
        INSERT INTO top_transaction
            (state, year, quarter, entity_name, entity_type, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
    "top_user": """
        INSERT INTO top_user
            (state, year, quarter, entity_name, entity_type, registered_users)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    "top_insurance": """
        INSERT INTO top_insurance
            (state, year, quarter, entity_name, entity_type, transaction_count, transaction_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
}

COLUMN_MAP = {
    "aggregated_transaction": [
        "state", "year", "quarter", "transaction_type",
        "transaction_count", "transaction_amount",
    ],
    "aggregated_user": [
        "state", "year", "quarter", "brand",
        "user_count", "user_percentage", "registered_users", "app_opens",
    ],
    "aggregated_insurance": [
        "state", "year", "quarter", "transaction_type",
        "transaction_count", "transaction_amount",
    ],
    "map_transaction": [
        "state", "year", "quarter", "district",
        "transaction_count", "transaction_amount",
    ],
    "map_user": [
        "state", "year", "quarter", "district",
        "registered_users", "app_opens",
    ],
    "map_insurance": [
        "state", "year", "quarter", "district",
        "transaction_count", "transaction_amount",
    ],
    "top_transaction": [
        "state", "year", "quarter", "entity_name", "entity_type",
        "transaction_count", "transaction_amount",
    ],
    "top_user": [
        "state", "year", "quarter", "entity_name", "entity_type",
        "registered_users",
    ],
    "top_insurance": [
        "state", "year", "quarter", "entity_name", "entity_type",
        "transaction_count", "transaction_amount",
    ],
}


def get_connection(with_db=True):
    cfg = DB_CONFIG.copy()
    if not with_db:
        cfg.pop("database", None)
    return mysql.connector.connect(**cfg)


def create_database():
    conn = get_connection(with_db=False)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"[✓] Database '{DB_CONFIG['database']}' ready.")


def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    for name, ddl in CREATE_TABLE_SQL.items():
        cur.execute(f"DROP TABLE IF EXISTS {name}")
        cur.execute(ddl)
    conn.commit()
    cur.close()
    conn.close()
    print("[✓] All 9 tables created.")


def load_table(table_name: str, df: pd.DataFrame):
    if df.empty:
        print(f"  ⚠  {table_name} – empty DataFrame, skipping.")
        return
    conn = get_connection()
    cur = conn.cursor()
    cols = COLUMN_MAP[table_name]
    sql = INSERT_SQL[table_name]
    data = [tuple(row[c] for c in cols) for _, row in df.iterrows()]
    cur.executemany(sql, data)
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✓  {table_name} – {len(data):,} rows inserted.")


# MAIN

def main():
    print("=" * 60)
    print("  PhonePe Pulse — ETL Pipeline")
    print("=" * 60)

    # 1. Clone
    clone_repo()

    # 2. Extract & Transform
    print("\n[…] Extracting & transforming JSON data …")
    tables = {
        "aggregated_transaction": extract_aggregated_transaction(),
        "aggregated_user": extract_aggregated_user(),
        "aggregated_insurance": extract_aggregated_insurance(),
        "map_transaction": extract_map_transaction(),
        "map_user": extract_map_user(),
        "map_insurance": extract_map_insurance(),
        "top_transaction": extract_top_transaction(),
        "top_user": extract_top_user(),
        "top_insurance": extract_top_insurance(),
    }

    # 3. Load
    print("\n[…] Loading into MySQL …")
    create_database()
    create_tables()
    for name, df in tables.items():
        load_table(name, df)

    print("\n" + "=" * 60)
    print("  ETL complete — all data is in MySQL!")
    print("=" * 60)


if __name__ == "__main__":
    main()