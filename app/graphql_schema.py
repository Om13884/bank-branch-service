import strawberry
from typing import Optional, List
from sqlalchemy.orm import Session
from strawberry.types import Info
from .models import Bank, Branch
from .schemas import BankOut, BranchOut

@strawberry.type
class BankType:
    id: int
    name: str

@strawberry.type
class BranchType:
    ifsc: str
    branch: str
    address: str
    city: str
    district: str
    state: str
    bank: BankType

@strawberry.type
class BranchConnection:
    total: int
    items: List[BranchType]

def to_bank_type(b: Bank) -> BankType:
    return BankType(id=b.id, name=b.name)

def to_branch_type(br: Branch) -> BranchType:
    return BranchType(
        ifsc=br.ifsc,
        branch=br.branch,
        address=br.address,
        city=br.city,
        district=br.district,
        state=br.state,
        bank=to_bank_type(br.bank),
    )

@strawberry.type
class Query:
    @strawberry.field
    def branches(self, info: Info, limit: int = 20, offset: int = 0, city: Optional[str] = None) -> BranchConnection:
        db: Session = info.context["db"]
        q = db.query(Branch).join(Bank)
        if city:
            q = q.filter(Branch.city == city)
        total = q.count()
        items = q.order_by(Branch.ifsc).offset(offset).limit(limit).all()
        return BranchConnection(total=total, items=[to_branch_type(b) for b in items])

    @strawberry.field
    def branch(self, info: Info, ifsc: str) -> Optional[BranchType]:
        db: Session = info.context["db"]
        br = db.query(Branch).join(Bank).filter(Branch.ifsc == ifsc).first()
        return to_branch_type(br) if br else None

schema = strawberry.Schema(query=Query)