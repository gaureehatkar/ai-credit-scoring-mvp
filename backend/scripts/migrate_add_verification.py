import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
import sqlalchemy as sa

with engine.connect() as conn:
    result = conn.execute(sa.text("PRAGMA table_info(users)"))
    cols = [row[1] for row in result]
    print("Existing columns:", cols)

    if "is_verified" not in cols:
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 0"))
        print("Added is_verified")

    if "verification_token" not in cols:
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN verification_token VARCHAR"))
        print("Added verification_token")

    # Mark existing users as verified so they can still log in
    conn.execute(sa.text("UPDATE users SET is_verified = 1 WHERE is_verified = 0"))
    print("Marked existing users as verified")

    conn.commit()
    print("Migration complete")
