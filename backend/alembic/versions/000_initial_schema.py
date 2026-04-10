"""Initial schema — create all base tables.

Revision ID: 000
Revises: None (base migration)
Create Date: 2026-04-10

Creates:
- users
- drivers
- ratings
- ride_contacts
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers
revision = '000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create all base tables."""

    # ── users ──────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='student'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])

    # ── drivers ────────────────────────────────────────────────────────
    op.create_table(
        'drivers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('vehicle_type', sa.String(20), nullable=False),
        sa.Column('vehicle_details', sa.String(200), nullable=True),
        sa.Column('service_area', sa.String(200), nullable=True),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('avg_rating', sa.Numeric(3, 2), nullable=False, server_default='0.0'),
        sa.Column('total_ratings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_drivers_email', 'drivers', ['email'], unique=True)
    op.create_index('ix_drivers_vehicle_type', 'drivers', ['vehicle_type'])
    op.create_index('ix_drivers_is_available', 'drivers', ['is_available'])
    op.create_index('ix_drivers_is_active', 'drivers', ['is_active'])

    # ── ratings ────────────────────────────────────────────────────────
    op.create_table(
        'ratings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('driver_id', UUID(as_uuid=True),
                  sa.ForeignKey('drivers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.SmallInteger(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint('rating BETWEEN 1 AND 5', name='ck_rating_range'),
        sa.UniqueConstraint('driver_id', 'student_id', name='uq_driver_student_rating'),
    )
    op.create_index('ix_ratings_driver_id', 'ratings', ['driver_id'])
    op.create_index('ix_ratings_student_id', 'ratings', ['student_id'])

    # ── ride_contacts ──────────────────────────────────────────────────
    op.create_table(
        'ride_contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('student_id', UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('driver_id', UUID(as_uuid=True),
                  sa.ForeignKey('drivers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contacted_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_ride_contacts_student_id', 'ride_contacts', ['student_id'])
    op.create_index('ix_ride_contacts_driver_id', 'ride_contacts', ['driver_id'])


def downgrade():
    """Drop all base tables."""
    op.drop_table('ride_contacts')
    op.drop_table('ratings')
    op.drop_table('drivers')
    op.drop_table('users')
