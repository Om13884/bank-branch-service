import csv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import engine, Base, SessionLocal
from app.models import Bank, Branch

def ingest(branches_csv: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    inserted_banks = set()   # keep track of seen banks

    try:
        with open(branches_csv, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                bank_id = int(row["bank_id"])
                bank_name = row["bank_name"].strip()

                # insert bank only once
                if bank_id not in inserted_banks:
                    bank = db.query(Bank).filter(Bank.id == bank_id).first()
                    if not bank:
                        db.add(Bank(id=bank_id, name=bank_name))
                    inserted_banks.add(bank_id)

                # insert branch if not exists
                ifsc = row["ifsc"].strip()
                exists_branch = db.query(Branch).filter(Branch.ifsc == ifsc).first()
                if not exists_branch:
                    db.add(Branch(
                        ifsc=ifsc,
                        bank_id=bank_id,
                        branch=row["branch"].strip(),
                        address=row["address"].strip(),
                        city=row["city"].strip(),
                        district=row["district"].strip(),
                        state=row["state"].strip(),
                    ))

            try:
                db.commit()
            except IntegrityError:
                db.rollback()  # skip duplicates
                print("⚠️ Skipped duplicate entries")

    finally:
        db.close()


if __name__ == "__main__":
    ingest("data/bank_branches.csv")
