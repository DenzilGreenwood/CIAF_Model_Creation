"""Initial schema from SQLite to PostgreSQL migration.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-15

This migration defines the complete CIAF proof store schema for PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""

    # OUTPUT_TAGS TABLE
    op.create_table(
        'output_tags',
        sa.Column('tag_id', sa.VARCHAR(36), nullable=False),
        sa.Column('session_id', sa.VARCHAR(100), nullable=False),
        sa.Column('output_content_hash', sa.VARCHAR(64), nullable=False),
        sa.Column('inference_receipt_id', sa.VARCHAR(100), nullable=False),
        sa.Column('inference_type', sa.VARCHAR(30), nullable=False),
        sa.Column('model_name', sa.VARCHAR(100)),
        sa.Column('agent_ids', postgresql.JSONB(), nullable=False),
        sa.Column('organization_id', sa.VARCHAR(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('policies_applied', postgresql.JSONB(), nullable=False),
        sa.Column('risk_level', sa.VARCHAR(20), nullable=False),
        sa.Column('task_batch_id', sa.VARCHAR(36)),
        sa.Column('task_batch_merkle_root', sa.VARCHAR(64)),
        sa.Column('task_batch_proof', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('tag_id'),
        sa.UniqueConstraint('output_content_hash', name='ux_output_tags_content_hash')
    )

    # Indexes for common queries
    op.create_index('idx_output_tags_org_id', 'output_tags', ['organization_id'])
    op.create_index('idx_output_tags_created_at', 'output_tags', ['created_at'])
    op.create_index('idx_output_tags_task_batch_id', 'output_tags', ['task_batch_id'])
    op.create_index('idx_output_tags_inference_type', 'output_tags', ['inference_type'])

    # TASK_BATCHES TABLE
    op.create_table(
        'task_batches',
        sa.Column('batch_id', sa.VARCHAR(36), nullable=False),
        sa.Column('session_id', sa.VARCHAR(100), nullable=False),
        sa.Column('organization_id', sa.VARCHAR(100), nullable=False),
        sa.Column('merkle_root', sa.VARCHAR(64), nullable=False),
        sa.Column('leaf_count', sa.Integer(), nullable=False),
        sa.Column('root_timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('batch_id'),
        sa.UniqueConstraint('merkle_root', name='ux_task_batches_merkle_root')
    )

    op.create_index('idx_task_batches_org_id', 'task_batches', ['organization_id'])
    op.create_index('idx_task_batches_created_at', 'task_batches', ['created_at'])

    # ORG_BATCH_WINDOWS TABLE
    op.create_table(
        'org_batch_windows',
        sa.Column('window_id', sa.VARCHAR(36), nullable=False),
        sa.Column('organization_id', sa.VARCHAR(100), nullable=False),
        sa.Column('batch_id', sa.VARCHAR(36), nullable=False),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('window_end', sa.DateTime(), nullable=False),
        sa.Column('lcm_status', sa.VARCHAR(20), nullable=False),
        sa.Column('proof_token', sa.VARCHAR(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('window_id'),
        sa.ForeignKeyConstraint(['batch_id'], ['task_batches.batch_id'], ondelete='CASCADE')
    )

    op.create_index('idx_org_batch_windows_org_id', 'org_batch_windows', ['organization_id'])
    op.create_index('idx_org_batch_windows_batch_id', 'org_batch_windows', ['batch_id'])
    op.create_index('idx_org_batch_windows_created_at', 'org_batch_windows', ['created_at'])

    # AGENT_ACTIONS TABLE (WORM - Write-Once-Read-Many, INSERT ONLY)
    op.create_table(
        'agent_actions',
        sa.Column('action_id', sa.VARCHAR(36), nullable=False),
        sa.Column('tag_id', sa.VARCHAR(36), nullable=False),
        sa.Column('agent_id', sa.VARCHAR(100), nullable=False),
        sa.Column('action_type', sa.VARCHAR(50), nullable=False),
        sa.Column('action_details', postgresql.JSONB()),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('action_id'),
        sa.ForeignKeyConstraint(['tag_id'], ['output_tags.tag_id'], ondelete='CASCADE')
    )

    op.create_index('idx_agent_actions_tag_id', 'agent_actions', ['tag_id'])
    op.create_index('idx_agent_actions_agent_id', 'agent_actions', ['agent_id'])
    op.create_index('idx_agent_actions_created_at', 'agent_actions', ['created_at'])

    # VERIFICATION_EVENTS TABLE (Read-only tracking)
    op.create_table(
        'verification_events',
        sa.Column('event_id', sa.VARCHAR(36), nullable=False),
        sa.Column('tag_id', sa.VARCHAR(36), nullable=False),
        sa.Column('verifier_id', sa.VARCHAR(100)),
        sa.Column('verified_at', sa.DateTime(), nullable=False),
        sa.Column('verification_result', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('event_id'),
        sa.ForeignKeyConstraint(['tag_id'], ['output_tags.tag_id'], ondelete='CASCADE')
    )

    op.create_index('idx_verification_events_tag_id', 'verification_events', ['tag_id'])
    op.create_index('idx_verification_events_created_at', 'verification_events', ['created_at'])

    # ORGANIZATIONS TABLE (Reference data)
    op.create_table(
        'organizations',
        sa.Column('organization_id', sa.VARCHAR(100), nullable=False),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('industry', sa.VARCHAR(100)),
        sa.Column('region', sa.VARCHAR(2)),
        sa.Column('api_key_hash', sa.VARCHAR(64), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('organization_id'),
        sa.UniqueConstraint('api_key_hash', name='ux_organizations_api_key_hash')
    )

    op.create_index('idx_organizations_is_active', 'organizations', ['is_active'])

    print("✅ Initial schema created successfully!")


def downgrade() -> None:
    """Drop all tables (rollback)."""

    # Drop in reverse order (foreign key constraints first)
    op.drop_table('verification_events')
    op.drop_table('agent_actions')
    op.drop_table('org_batch_windows')
    op.drop_table('task_batches')
    op.drop_table('output_tags')
    op.drop_table('organizations')

    print("✅ Schema rollback completed!")
