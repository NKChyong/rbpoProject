"""Seed database with sample data."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.adapters.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.domain.models import Entry, EntryKind, EntryStatus, User, UserRole


async def seed_database() -> None:
    """Seed database with sample data."""
    print("Seeding database...")

    async with AsyncSessionLocal() as db:
        # Create sample users
        users_data = [
            {
                "email": "alice@example.com",
                "username": "alice",
                "password": "password123",
                "role": UserRole.USER.value,
            },
            {
                "email": "bob@example.com",
                "username": "bob",
                "password": "password123",
                "role": UserRole.USER.value,
            },
            {
                "email": "admin@example.com",
                "username": "admin",
                "password": "admin123",
                "role": UserRole.ADMIN.value,
            },
        ]

        users = []
        for user_data in users_data:
            # Check if user exists
            from sqlalchemy import select

            result = await db.execute(
                select(User).where(User.username == user_data["username"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                users.append(existing_user)
                continue

            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            db.add(user)
            users.append(user)
            print(f"Created user: {user_data['username']}")

        await db.flush()

        # Create sample entries for Alice
        alice = users[0]
        entries_data = [
            {
                "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                "kind": EntryKind.BOOK.value,
                "link": "https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882",
                "status": EntryStatus.IN_PROGRESS.value,
                "description": (
                    "Even bad code can function. But if code isn't clean, "
                    "it can bring a development organization to its knees."
                ),
            },
            {
                "title": "FastAPI Tutorial",
                "kind": EntryKind.ARTICLE.value,
                "link": "https://fastapi.tiangolo.com/tutorial/",
                "status": EntryStatus.COMPLETED.value,
                "description": "Official FastAPI tutorial with all the features",
            },
            {
                "title": "Python AsyncIO: Understanding Async/Await",
                "kind": EntryKind.VIDEO.value,
                "link": "https://www.youtube.com/watch?v=t5Bo1Je9EmE",
                "status": EntryStatus.TO_READ.value,
                "description": "Deep dive into Python's async capabilities",
            },
            {
                "title": "The Changelog Podcast",
                "kind": EntryKind.PODCAST.value,
                "link": "https://changelog.com/podcast",
                "status": EntryStatus.TO_READ.value,
                "description": "Software development, open source, building startups",
            },
            {
                "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
                "kind": EntryKind.BOOK.value,
                "link": "https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612",
                "status": EntryStatus.TO_READ.value,
                "description": "The Gang of Four design patterns book",
            },
        ]

        for entry_data in entries_data:
            entry = Entry(
                title=entry_data["title"],
                kind=entry_data["kind"],
                link=entry_data["link"],
                status=entry_data["status"],
                description=entry_data["description"],
                owner_id=alice.id,
            )
            db.add(entry)
            print(f"Created entry: {entry_data['title'][:50]}...")

        # Create sample entries for Bob
        bob = users[1]
        bob_entries = [
            {
                "title": "The Pragmatic Programmer",
                "kind": EntryKind.BOOK.value,
                "status": EntryStatus.TO_READ.value,
                "description": "Your Journey To Mastery",
            },
            {
                "title": "Introduction to Algorithms",
                "kind": EntryKind.BOOK.value,
                "status": EntryStatus.IN_PROGRESS.value,
                "description": "CLRS book on algorithms",
            },
        ]

        for entry_data in bob_entries:
            entry = Entry(
                title=entry_data["title"],
                kind=entry_data["kind"],
                status=entry_data["status"],
                description=entry_data["description"],
                owner_id=bob.id,
            )
            db.add(entry)
            print(f"Created entry: {entry_data['title']}")

        await db.commit()
        print("\nDatabase seeded successfully!")
        print("\nSample credentials:")
        print("  User 1: alice / password123")
        print("  User 2: bob / password123")
        print("  Admin: admin / admin123")


if __name__ == "__main__":
    asyncio.run(seed_database())
