"""Script to create an admin user."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.adapters.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.domain.models import User, UserRole


async def create_admin_user(email: str, username: str, password: str) -> None:
    """Create an admin user."""
    async with AsyncSessionLocal() as db:
        # Check if user exists
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User {username} already exists!")
            return

        # Create admin user
        admin = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN.value,
            is_active=True,
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        print("Admin user created successfully!")
        print(f"  ID: {admin.id}")
        print(f"  Username: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  Role: {admin.role}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scripts/create_admin.py <email> <username> <password>")
        print("Example: python scripts/create_admin.py admin@example.com admin adminpass123")
        sys.exit(1)

    email = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    asyncio.run(create_admin_user(email, username, password))
