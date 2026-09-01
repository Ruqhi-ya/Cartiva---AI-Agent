import ast
import csv
from pathlib import Path

from app.database import SessionLocal
from app.models import Product


CSV_FILE = Path(
    r"C:\Users\Umme Hani\Downloads\archive\cartiva_data\cartiva_clean_products.csv"
)


def parse_list(value):
    """Convert a CSV string representation of a list into a Python list."""
    if not value:
        return []

    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else []
    except (ValueError, SyntaxError):
        return []


def import_products():
    db = SessionLocal()

    try:
        with open(
            CSV_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            inserted = 0
            skipped = 0

            for row in reader:

                product_id = int(row["id"])

                # Skip products that already exist
                existing = (
                    db.query(Product)
                    .filter(Product.id == product_id)
                    .first()
                )

                if existing:
                    skipped += 1
                    continue

                product = Product(
                    id=product_id,
                    name=row["name"],
                    description=row["description"],
                    category=row["category"],
                    price=float(row["price"]),
                    image=row["image"].split(",")[0].strip(),
                    stock=int(row["stock"]),
                    tags=parse_list(row["tags"]),
                    related_ids=parse_list(row["related_ids"]),
                    is_premium=row["is_premium"].lower() == "true",
                )

                db.add(product)
                inserted += 1

            db.commit()

            print("Import complete!")
            print(f"Products inserted: {inserted}")
            print(f"Products skipped: {skipped}")

    except Exception as e:
        db.rollback()
        print("Import failed!")
        print(f"Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    import_products()