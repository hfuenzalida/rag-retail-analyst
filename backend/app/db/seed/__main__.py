"""Load demo retail seed data into PostgreSQL."""

import argparse

from app.core.config import get_settings
from app.db.connection import get_connection, init_pool
from app.db.seed.demo_retail import CLIENT_ID, seed_demo_retail


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo retail data")
    parser.add_argument("--client-id", default=CLIENT_ID)
    args = parser.parse_args()

    settings = get_settings()
    init_pool(settings)
    with get_connection(settings) as conn:
        seed_demo_retail(conn, client_id=args.client_id)
    print(f"Seeded demo data for client_id={args.client_id}")


if __name__ == "__main__":
    main()
