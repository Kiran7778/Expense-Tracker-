from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import get_connection, init_db
from models import *


app = FastAPI(
    title="💰 Expense Tracker API",
    version="1.0.0"
)

# CORS (for frontend like Streamlit/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ───────── STARTUP DB ─────────
@app.on_event("startup")
def startup():
    init_db()


# ───────── HOME ─────────
@app.get("/")
def home():
    return {"message": "Expense Tracker API is running 🚀"}


# ───────── CREATE ─────────
@app.post("/expenses", response_model=MessageResponse)
def add_expense(expense: ExpenseCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (title, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, (expense.title, expense.amount, expense.category, expense.date, expense.description))

    conn.commit()
    conn.close()

    return {"message": "Expense added successfully"}


# ───────── GET ALL ─────────
@app.get("/expenses", response_model=ExpenseListResponse)
def get_expenses(
    category: str = None,
    min_amount: float = None,
    max_amount: float = None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if min_amount is not None:
        query += " AND amount >= ?"
        params.append(min_amount)

    if max_amount is not None:
        query += " AND amount <= ?"
        params.append(max_amount)

    query += " ORDER BY date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    expenses = [
        ExpenseResponse(**row) for row in rows
    ]

    conn.close()

    return {"expenses": expenses, "count": len(expenses)}


# ───────── SINGLE ─────────
@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(404, "Expense not found")

    return ExpenseResponse(**row)


# ───────── UPDATE ─────────
@app.put("/expenses/{expense_id}", response_model=MessageResponse)
def update_expense(expense_id: int, expense: ExpenseUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(404, "Expense not found")

    updates = []
    params = []

    data = expense.model_dump(exclude_none=True)

    if not data:
        raise HTTPException(400, "No fields to update")

    for k, v in data.items():
        updates.append(f"{k}=?")
        params.append(v)

    params.append(expense_id)

    query = f"UPDATE expenses SET {', '.join(updates)} WHERE id=?"
    cursor.execute(query, params)

    conn.commit()
    conn.close()

    return {"message": "Expense updated successfully"}


# ───────── DELETE ─────────
@app.delete("/expenses/{expense_id}", response_model=MessageResponse)
def delete_expense(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

    return {"message": "Expense deleted successfully"}


# ───────── TOTAL ─────────
@app.get("/total", response_model=TotalResponse)
def total():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) as total, COUNT(*) as count FROM expenses")
    row = cursor.fetchone()

    conn.close()

    return {"total": row["total"] or 0, "count": row["count"]}


# ───────── SUMMARY ─────────
@app.get("/summary", response_model=SummaryResponse)
def summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) total, COUNT(*) count FROM expenses")
    totals = cursor.fetchone()

    cursor.execute("""
        SELECT category, SUM(amount) total, COUNT(*) count
        FROM expenses
        GROUP BY category
    """)

    categories = [
        CategorySummary(**row) for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "total_spent": totals["total"] or 0,
        "total_count": totals["count"],
        "categories": categories
    }