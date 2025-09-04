from pydantic import BaseModel

class BankOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class BranchOut(BaseModel):
    ifsc: str
    branch: str
    address: str
    city: str
    district: str
    state: str
    bank: BankOut

    class Config:
        from_attributes = True

class PaginatedBranches(BaseModel):
    total: int
    items: list[BranchOut]