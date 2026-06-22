import json
import os
from typing import Dict


def save_analysis_result(result: Dict) -> Dict:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return {"persisted": False, "reason": "DATABASE_URL is not configured"}

    import psycopg

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                create table if not exists candidate_analyses (
                    id bigserial primary key,
                    session_id text,
                    resume_uri text,
                    result jsonb not null,
                    created_at timestamptz default now()
                )
                """
            )
            cursor.execute(
                """
                insert into candidate_analyses (session_id, resume_uri, result)
                values (%s, %s, %s)
                returning id
                """,
                (
                    result.get("session_id"),
                    result.get("resume_uri"),
                    json.dumps(result),
                ),
            )
            analysis_id = cursor.fetchone()[0]
        connection.commit()

    return {"persisted": True, "analysis_id": analysis_id}
