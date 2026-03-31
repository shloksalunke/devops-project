"""Add RTO verification system and driver documents table.

Revision ID: 001
Revises: None
Create Date: 2026-03-28 10:00:00.000000

This migration adds:
1. Verification fields to drivers table (verification_status, verification_notes, verified_at, verified_by)
2. New driver_documents table for tracking RTO documents (ID, LICENSE, RC, INSURANCE)
3. Indexes for performance optimization
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add verification fields to drivers table."""
    # Add columns to drivers table
    op.add_column('drivers', sa.Column('verification_status', sa.String(20), nullable=False, server_default='PENDING'))
    op.add_column('drivers', sa.Column('verification_notes', sa.String(1000), nullable=True))
    op.add_column('drivers', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('drivers', sa.Column('verified_by', sa.UUID(), nullable=True))
    
    # Add foreign key constraint for verified_by
    op.create_foreign_key(
        'fk_drivers_verified_by',
        'drivers',
        'users',
        ['verified_by'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create driver_documents table
    op.create_table(
        'driver_documents',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.func.gen_random_uuid()),
        sa.Column('driver_id', sa.UUID(), nullable=False),
        sa.Column('document_type', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('rejection_reason', sa.String(500), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.UUID(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint("document_type IN ('ID', 'LICENSE', 'RC', 'INSURANCE')", name='ck_document_type'),
        sa.CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED')", name='ck_document_status'),
    )
    
    # Add indexes
    op.create_index('idx_drivers_verification_status', 'drivers', ['verification_status'])
    op.create_index('idx_driver_documents_driver_id', 'driver_documents', ['driver_id'])
    op.create_index('idx_driver_documents_document_type', 'driver_documents', ['document_type'])
    op.create_index('idx_driver_documents_status', 'driver_documents', ['status'])


def downgrade():
    """Remove verification fields and driver_documents table."""
    # Drop indexes
    op.drop_index('idx_driver_documents_status', table_name='driver_documents')
    op.drop_index('idx_driver_documents_document_type', table_name='driver_documents')
    op.drop_index('idx_driver_documents_driver_id', table_name='driver_documents')
    op.drop_index('idx_drivers_verification_status', table_name='drivers')
    
    # Drop driver_documents table
    op.drop_table('driver_documents')
    
    # Drop foreign key and columns from drivers table
    op.drop_constraint('fk_drivers_verified_by', 'drivers', type_='foreignkey')
    op.drop_column('drivers', 'verified_by')
    op.drop_column('drivers', 'verified_at')
    op.drop_column('drivers', 'verification_notes')
    op.drop_column('drivers', 'verification_status')
