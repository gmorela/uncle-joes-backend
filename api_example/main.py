"""
Uncle Joe's Coffee Company — FastAPI login example

Demonstrates how to accept credentials over HTTP, hash the submitted
password with bcrypt, and construct a parameterized BigQuery query to
look up the matching member.

Setup:
    poetry install

Run:
    poetry run uvicorn main:app --reload

Then POST to http://127.0.0.1:8000/login
"""

import bcrypt
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI(title="Uncle Joe's Coffee API")

# Replace with your GCP project ID
GCP_PROJECT = "uncle-joes-493215"
DATASET = "uncle_joes"

client = bigquery.Client(project=GCP_PROJECT)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(body: LoginRequest):
    # 1. Hash the submitted password so we never handle it in plain text
    #    beyond this point.  bcrypt.hashpw produces a new hash every call
    #    (random salt), so we can't compare hashes directly — we use
    #    bcrypt.checkpw() against the stored hash retrieved from the DB.
    submitted_bytes = body.password.encode("utf-8")
    _ = bcrypt.hashpw(submitted_bytes, bcrypt.gensalt())  # shown for illustration

    # 2. Build a parameterized query to fetch the member's stored hash.
    #    Never interpolate user input directly into SQL strings.
    query = """
        SELECT id, first_name, last_name, email, password
        FROM `{project}.{dataset}.members`
        WHERE email = @email
        LIMIT 1
    """.format(project=GCP_PROJECT, dataset=DATASET)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", body.email),
        ]
    )

    results = list(client.query(query, job_config=job_config).result())

    if not results:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    row = results[0]
    stored_hash: str = row["password"]

    # 3. Verify the submitted password against the bcrypt hash from the DB.
    if not bcrypt.checkpw(submitted_bytes, stored_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {
        "authenticated": True,
        "member_id": row["id"],
        "name": f"{row['first_name']} {row['last_name']}",
        "email": row["email"],
    }


# Helper function to run queries and return results as a list of dicts
def run_query(query: str, params: list = []):
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    query_job = client.query(query, job_config=job_config)
    return [dict(row) for row in query_job]

# --- LOCATIONS ---

@app.get("/locations")
def get_locations():
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.locations`"
    return run_query(query)

@app.get("/locations/{location_id}")
def get_location(location_id: str):
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.locations` WHERE id = @id"
    params = [bigquery.ScalarQueryParameter("id", "STRING", location_id)]
    results = run_query(query, params)
    if not results:
        raise HTTPException(status_code=404, detail="Location not found")
    return results[0]

# --- MEMBERS ---

@app.get("/members")
def get_members():
    # We exclude passwords here for security best practices
    query = f"SELECT id, first_name, last_name, email, phone_number, home_store FROM `{GCP_PROJECT}.{DATASET}.members`"
    return run_query(query)

@app.get("/members/{member_id}")
def get_member(member_id: str):
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.members` WHERE id = @id"
    params = [bigquery.ScalarQueryParameter("id", "STRING", member_id)]
    results = run_query(query, params)
    if not results:
        raise HTTPException(status_code=404, detail="Member not found")
    return results[0]

@app.get("/members/store/{location_id}")
def get_members_by_store(location_id: str):
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.members` WHERE home_store = @store_id"
    params = [bigquery.ScalarQueryParameter("store_id", "STRING", location_id)]
    return run_query(query, params)

# --- ORDERS ---

@app.get("/orders")
def get_all_orders():
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.orders` ORDER BY order_date DESC"
    return run_query(query)

@app.get("/orders/location/{location_id}")
def get_orders_by_location(location_id: str):
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.orders` WHERE store_id = @store_id"
    params = [bigquery.ScalarQueryParameter("store_id", "STRING", location_id)]
    return run_query(query, params)

@app.get("/orders/member/{member_id}")
def get_orders_by_member(member_id: str):
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.orders` WHERE member_id = @member_id"
    params = [bigquery.ScalarQueryParameter("member_id", "STRING", member_id)]
    return run_query(query, params)

# --- ORDER ITEMS & MENU ---

@app.get("/menu")
def get_menu():
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.menu_items`"
    return run_query(query)

@app.get("/order-items/{order_id}")
def get_items_for_order(order_id: str):
    query = f"SELECT * FROM `{GCP_PROJECT}.{DATASET}.order_items` WHERE order_id = @order_id"
    params = [bigquery.ScalarQueryParameter("order_id", "STRING", order_id)]
    return run_query(query, params)

@app.get("/menu/order/{order_id}")
def get_menu_details_for_order(order_id: str):
    # This joins the order_items and menu_items tables to show what was actually bought
    query = f"""
        SELECT m.name, m.category, oi.quantity, oi.price, oi.size
        FROM `{GCP_PROJECT}.{DATASET}.order_items` AS oi
        JOIN `{GCP_PROJECT}.{DATASET}.menu_items` AS m ON oi.menu_item_id = m.id
        WHERE oi.order_id = @order_id
    """
    params = [bigquery.ScalarQueryParameter("order_id", "STRING", order_id)]
    return run_query(query, params)