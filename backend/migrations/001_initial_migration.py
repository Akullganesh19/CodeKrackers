"""initial migration

Revision ID: 001
Revises:
Create Date: 2024-05-21 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Users Table
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), server_default="citizen"),
        sa.Column("rbac_level", sa.Integer(), server_default="1"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("safety_score", sa.Float(), server_default="100.0"),
        sa.Column("scams_avoided", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # 2. Threats Table
    op.create_table(
        "threats",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("type", sa.String(50)),
        sa.Column("severity", sa.String(50)),
        sa.Column("status", sa.String(50), server_default="detected"),
        sa.Column("raw_content", sa.Text()),
        sa.Column("risk_score", sa.Float()),
        sa.Column("confidence", sa.Float()),
        sa.Column("caller_id", sa.String(20)),
        sa.Column("sender_id", sa.String(50)),
        sa.Column("suspicious_urls", sa.JSON()),
        sa.Column("ipc_sections", sa.JSON()),
        sa.Column("is_reported", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("detected_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("evidence_hash", sa.String(128)),
        sa.Column("extra_info", sa.JSON()),
    )

    # Composite Index for Scammer Audit Performance
    op.create_index(
        "ix_threats_caller_id_detected_at", "threats", ["caller_id", "detected_at"]
    )

    # 3. Evidence Chain Table (Forensic Ledger)
    op.create_table(
        "evidence_chain",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("threat_id", sa.String(36), sa.ForeignKey("threats.id")),
        sa.Column("block_index", sa.Integer(), autoincrement=True, unique=True),
        sa.Column("previous_hash", sa.String(128)),
        sa.Column("current_hash", sa.String(128), unique=True),
        sa.Column("payload", sa.JSON()),
        sa.Column("digital_signature", sa.String(256)),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("block_type", sa.String(50)),
    )

    # 4. FIRs Table
    op.create_table(
        "firs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_number", sa.String(50), unique=True),
        sa.Column("threat_id", sa.String(36), sa.ForeignKey("threats.id")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("pdf_path", sa.String(500)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # 5. Honeypot Sessions Table
    op.create_table(
        "honeypot_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("threat_id", sa.String(36), sa.ForeignKey("threats.id")),
        sa.Column("scammer_number", sa.String(20)),
        sa.Column("session_start", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("session_end", sa.DateTime()),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("evidence_collected", sa.JSON()),
    )

    # 6. Score History Table (For Trends)
    op.create_table(
        "score_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("score", sa.Float()),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("score_history")
    op.drop_table("honeypot_sessions")
    op.drop_table("firs")
    op.drop_table("evidence_chain")
    op.drop_index("ix_threats_caller_id_detected_at", table_name="threats")
    op.drop_table("threats")
    op.drop_table("users")
