"""Normalize review tasks into relational tables.

Revision ID: 002
Revises: 001
Create Date: 2026-07-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("stars", sa.Integer(), server_default="0", nullable=False),
        sa.Column("forks", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "primary_language",
            sa.String(length=100),
            server_default="Unknown",
            nullable=False,
        ),
        sa.Column("file_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("dir_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_lines", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )

    op.create_table(
        "repository_languages",
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("repository_id", "name"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("progress", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "current_step",
            sa.String(length=255),
            server_default="",
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("report_markdown", sa.Text(), nullable=True),
        sa.Column("overall_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("security_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "performance_score", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column(
            "maintainability_score", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column(
            "code_quality_score", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column(
            "architecture_score", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("progress BETWEEN 0 AND 100", name="ck_reviews_progress"),
        sa.CheckConstraint(
            "status IN ('pending', 'in-progress', 'completed', 'failed')",
            name="review_status",
        ),
        sa.CheckConstraint(
            "overall_score BETWEEN 0 AND 100", name="ck_reviews_overall_score"
        ),
        sa.CheckConstraint(
            "security_score BETWEEN 0 AND 100", name="ck_reviews_security_score"
        ),
        sa.CheckConstraint(
            "performance_score BETWEEN 0 AND 100",
            name="ck_reviews_performance_score",
        ),
        sa.CheckConstraint(
            "maintainability_score BETWEEN 0 AND 100",
            name="ck_reviews_maintainability_score",
        ),
        sa.CheckConstraint(
            "code_quality_score BETWEEN 0 AND 100",
            name="ck_reviews_code_quality_score",
        ),
        sa.CheckConstraint(
            "architecture_score BETWEEN 0 AND 100",
            name="ck_reviews_architecture_score",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_repository_id", "reviews", ["repository_id"])
    op.create_index("ix_reviews_status", "reviews", ["status"])

    op.create_table(
        "review_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_key", sa.String(length=64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("estimated_time", sa.Integer(), server_default="0", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("position >= 0", name="ck_review_steps_position"),
        sa.CheckConstraint(
            "estimated_time >= 0", name="ck_review_steps_estimated_time"
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'in-progress', 'completed', 'failed')",
            name="step_status",
        ),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "review_id",
            "step_key",
            name="uq_review_steps_review_key",
        ),
    )
    op.create_index("ix_review_steps_review_id", "review_steps", ["review_id"])

    op.create_table(
        "review_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("extension", sa.String(length=50), server_default="", nullable=False),
        sa.Column("line_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("summary", sa.Text(), server_default="", nullable=False),
        sa.Column("score", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("line_count >= 0", name="ck_review_files_line_count"),
        sa.CheckConstraint("score BETWEEN 0 AND 100", name="ck_review_files_score"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "review_id",
            "path",
            name="uq_review_files_review_path",
        ),
    )
    op.create_index("ix_review_files_review_id", "review_files", ["review_id"])

    op.create_table(
        "review_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column(
            "file_path", sa.String(length=1024), server_default="", nullable=False
        ),
        sa.Column("line_number", sa.Integer(), server_default="0", nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("suggestion", sa.Text(), server_default="", nullable=False),
        sa.Column("code_snippet", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("line_number >= 0", name="ck_review_issues_line_number"),
        sa.CheckConstraint(
            "type IN "
            "('security', 'performance', 'maintainability', 'code-quality', 'architecture')",
            name="issue_type",
        ),
        sa.CheckConstraint(
            "severity IN ('critical', 'high', 'medium', 'low', 'info')",
            name="issue_severity",
        ),
        sa.ForeignKeyConstraint(["file_id"], ["review_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_issues_file_id", "review_issues", ["file_id"])
    op.create_index("ix_review_issues_review_id", "review_issues", ["review_id"])
    op.create_index("ix_review_issues_type", "review_issues", ["type"])
    op.create_index("ix_review_issues_severity", "review_issues", ["severity"])

    _migrate_legacy_data()
    op.drop_table("review_tasks")


def _migrate_legacy_data() -> None:
    uuid_from_md5 = (
        "CAST(substr(md5({value}), 1, 8) || '-' || "
        "substr(md5({value}), 9, 4) || '-' || "
        "substr(md5({value}), 13, 4) || '-' || "
        "substr(md5({value}), 17, 4) || '-' || "
        "substr(md5({value}), 21, 12) AS uuid)"
    )
    repository_uuid = uuid_from_md5.format(value="repository_url")

    op.execute(sa.text(f"""
            INSERT INTO repositories (
                id, url, owner, name, description, stars, forks,
                primary_language, file_count, dir_count, total_lines,
                last_updated_at, created_at, updated_at
            )
            SELECT DISTINCT ON (repository_url)
                {repository_uuid},
                repository_url,
                split_part(regexp_replace(repository_url, '^https://github.com/', ''), '/', 1),
                split_part(regexp_replace(repository_url, '^https://github.com/', ''), '/', 2),
                COALESCE(result->'repository'->>'description', ''),
                COALESCE((result->'repository'->>'stars')::integer, 0),
                COALESCE((result->'repository'->>'forks')::integer, 0),
                COALESCE(result->'repository'->>'primary_language', 'Unknown'),
                COALESCE((result->'repository'->>'file_count')::integer, 0),
                COALESCE((result->'repository'->>'dir_count')::integer, 0),
                COALESCE((result->'repository'->>'total_lines')::integer, 0),
                NULL,
                created_at,
                updated_at
            FROM review_tasks
            ORDER BY repository_url, updated_at DESC
            """))

    op.execute(sa.text(f"""
            INSERT INTO reviews (
                id, repository_id, status, progress, current_step,
                error_message, report_markdown, overall_score, security_score,
                performance_score, maintainability_score, code_quality_score,
                architecture_score, started_at, completed_at, created_at, updated_at
            )
            SELECT
                id,
                {repository_uuid},
                status,
                progress,
                current_step,
                error_message,
                report_markdown,
                COALESCE((result->'metrics'->>'overall_score')::integer, 0),
                COALESCE((result->'metrics'->>'security_score')::integer, 0),
                COALESCE((result->'metrics'->>'performance_score')::integer, 0),
                COALESCE((result->'metrics'->>'maintainability_score')::integer, 0),
                COALESCE((result->'metrics'->>'code_quality_score')::integer, 0),
                COALESCE((result->'metrics'->>'architecture_score')::integer, 0),
                CASE WHEN status <> 'pending' THEN created_at ELSE NULL END,
                CASE WHEN status IN ('completed', 'failed') THEN updated_at ELSE NULL END,
                created_at,
                updated_at
            FROM review_tasks
            """))

    op.execute(sa.text(f"""
            INSERT INTO repository_languages (repository_id, name)
            SELECT DISTINCT
                {repository_uuid},
                language.value
            FROM review_tasks
            CROSS JOIN LATERAL jsonb_array_elements_text(
                COALESCE(result->'repository'->'languages', '[]'::jsonb)
            ) AS language(value)
            ON CONFLICT DO NOTHING
            """))

    step_uuid = uuid_from_md5.format(
        value="task.id::text || ':step:' || step.value->>'id'"
    )
    op.execute(sa.text(f"""
            INSERT INTO review_steps (
                id, review_id, step_key, position, name, description,
                status, estimated_time, started_at, completed_at
            )
            SELECT
                {step_uuid},
                task.id,
                step.value->>'id',
                step.ordinality - 1,
                step.value->>'name',
                COALESCE(step.value->>'description', ''),
                COALESCE(step.value->>'status', 'pending'),
                COALESCE((step.value->>'estimated_time')::integer, 0),
                NULL,
                NULL
            FROM review_tasks AS task
            CROSS JOIN LATERAL jsonb_array_elements(task.steps)
                WITH ORDINALITY AS step(value, ordinality)
            """))

    file_uuid = uuid_from_md5.format(
        value="task.id::text || ':file:' || file.value->>'path'"
    )
    op.execute(sa.text(f"""
            INSERT INTO review_files (
                id, review_id, path, name, extension, line_count, summary, score
            )
            SELECT
                {file_uuid},
                task.id,
                file.value->>'path',
                file.value->>'name',
                COALESCE(file.value->>'extension', ''),
                COALESCE((file.value->>'lines')::integer, 0),
                COALESCE(file.value->>'summary', ''),
                COALESCE((file.value->>'score')::integer, 0)
            FROM review_tasks AS task
            CROSS JOIN LATERAL jsonb_array_elements(
                COALESCE(task.result->'files', '[]'::jsonb)
            ) AS file(value)
            """))

    issue_uuid = uuid_from_md5.format(
        value=(
            "task.id::text || ':issue:' || file.value->>'path' || ':' || "
            "issue.ordinality::text"
        )
    )
    op.execute(sa.text(f"""
            INSERT INTO review_issues (
                id, review_id, file_id, external_id, file_path, line_number,
                type, severity, title, description, suggestion, code_snippet, created_at
            )
            SELECT
                {issue_uuid},
                task.id,
                {file_uuid},
                issue.value->>'id',
                COALESCE(issue.value->>'file', file.value->>'path'),
                COALESCE((issue.value->>'line')::integer, 0),
                issue.value->>'type',
                issue.value->>'severity',
                issue.value->>'title',
                COALESCE(issue.value->>'description', ''),
                COALESCE(issue.value->>'suggestion', ''),
                issue.value->>'code',
                task.created_at
            FROM review_tasks AS task
            CROSS JOIN LATERAL jsonb_array_elements(
                COALESCE(task.result->'files', '[]'::jsonb)
            ) AS file(value)
            CROSS JOIN LATERAL jsonb_array_elements(
                COALESCE(file.value->'issues', '[]'::jsonb)
            ) WITH ORDINALITY AS issue(value, ordinality)
            """))


def downgrade() -> None:
    op.create_table(
        "review_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("repository_url", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("current_step", sa.String(length=255), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "steps",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("report_markdown", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(sa.text("""
            INSERT INTO review_tasks (
                id, repository_url, status, progress, current_step, error_message,
                steps, result, report_markdown, created_at, updated_at
            )
            SELECT
                review.id,
                repository.url,
                review.status,
                review.progress,
                review.current_step,
                review.error_message,
                COALESCE((
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'id', step.step_key,
                            'name', step.name,
                            'description', step.description,
                            'status', step.status,
                            'estimated_time', step.estimated_time
                        )
                        ORDER BY step.position
                    )
                    FROM review_steps AS step
                    WHERE step.review_id = review.id
                ), '[]'::jsonb),
                jsonb_build_object(
                    'id', review.id::text,
                    'repository_url', repository.url,
                    'repository', jsonb_build_object(
                        'id', repository.id::text,
                        'name', repository.name,
                        'owner', repository.owner,
                        'url', repository.url,
                        'description', repository.description,
                        'stars', repository.stars,
                        'forks', repository.forks,
                        'primary_language', repository.primary_language,
                        'languages', COALESCE((
                            SELECT jsonb_agg(language.name ORDER BY language.name)
                            FROM repository_languages AS language
                            WHERE language.repository_id = repository.id
                        ), '[]'::jsonb),
                        'file_count', repository.file_count,
                        'dir_count', repository.dir_count,
                        'total_lines', repository.total_lines,
                        'last_updated', ''
                    ),
                    'metrics', jsonb_build_object(
                        'overall_score', review.overall_score,
                        'security_score', review.security_score,
                        'performance_score', review.performance_score,
                        'maintainability_score', review.maintainability_score,
                        'code_quality_score', review.code_quality_score,
                        'architecture_score', review.architecture_score
                    ),
                    'files', COALESCE((
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'path', file.path,
                                'name', file.name,
                                'extension', file.extension,
                                'lines', file.line_count,
                                'summary', file.summary,
                                'score', file.score,
                                'issues', COALESCE((
                                    SELECT jsonb_agg(
                                        jsonb_build_object(
                                            'id', COALESCE(issue.external_id, issue.id::text),
                                            'file', issue.file_path,
                                            'line', issue.line_number,
                                            'type', issue.type,
                                            'severity', issue.severity,
                                            'title', issue.title,
                                            'description', issue.description,
                                            'suggestion', issue.suggestion,
                                            'code', issue.code_snippet
                                        )
                                    )
                                    FROM review_issues AS issue
                                    WHERE issue.file_id = file.id
                                ), '[]'::jsonb)
                            )
                            ORDER BY file.path
                        )
                        FROM review_files AS file
                        WHERE file.review_id = review.id
                    ), '[]'::jsonb),
                    'created_at', review.created_at,
                    'status', review.status,
                    'progress', review.progress,
                    'current_step', review.current_step
                ),
                review.report_markdown,
                review.created_at,
                review.updated_at
            FROM reviews AS review
            JOIN repositories AS repository ON repository.id = review.repository_id
            """))

    op.drop_table("review_issues")
    op.drop_table("review_files")
    op.drop_table("review_steps")
    op.drop_table("reviews")
    op.drop_table("repository_languages")
    op.drop_table("repositories")
