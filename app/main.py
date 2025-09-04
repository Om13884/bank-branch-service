from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import strawberry
from strawberry.fastapi import GraphQLRouter

from .database import Base, engine, get_db
from .models import Bank, Branch
from .schemas import BankOut, BranchOut, PaginatedBranches
from .graphql_schema import schema as gql_schema

app = FastAPI(title="Bank Branch Service", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ✅ FIX: GraphQL Router without forcing context at mount time
def get_context():
    db = next(get_db())
    return {"db": db}

graphql_app = GraphQLRouter(
    schema=gql_schema,
    graphiql=True,   # enables GraphiQL web UI
    context_getter=get_context
)

app.include_router(graphql_app, prefix="/gql")

# ---------------- REST Endpoints ----------------
@app.get("/banks", response_model=list[BankOut])
def list_banks(db: Session = Depends(get_db)):
    banks = db.query(Bank).order_by(Bank.name).all()
    return banks

@app.get("/branches/{ifsc}", response_model=BranchOut)
def get_branch(ifsc: str, db: Session = Depends(get_db)):
    br = db.query(Branch).join(Bank).filter(Branch.ifsc == ifsc).first()
    if not br:
        raise HTTPException(status_code=404, detail="Branch not found")
    return br

@app.get("/banks/{bank_id}/branches", response_model=PaginatedBranches)
def list_branches_for_bank(
    bank_id: int,
    city: str | None = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    q = db.query(Branch).join(Bank).filter(Branch.bank_id == bank_id)
    if city:
        q = q.filter(Branch.city == city)

    total = q.count()
    items = q.order_by(Branch.ifsc).offset(offset).limit(limit).all()
    return {"total": total, "items": items}

# ---------------- Custom Landing Page ----------------
@app.get("/", include_in_schema=False)
def root():
    html_content = """
    <html>
        <head>
            <title>Bank Branch API</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 80px; }
                h1 { color: #2E86C1; }
                a { display: block; margin: 10px; font-size: 18px; text-decoration: none; color: #117A65; }
                a:hover { text-decoration: underline; color: #0B5345; }
            </style>
        </head>
        <body>
            <h1>🚀 Bank Branch API is running</h1>
            <p>Select where you want to go:</p>
            <a href="/docs">Swagger Docs</a>
            <a href="/redoc">ReDoc Docs</a>
            <a href="/gql">GraphQL Playground</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
