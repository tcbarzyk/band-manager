"""Sync database with current models for Supabase auth

Revision ID: 1b4fbfae822b
Revises: 36f0b5621c0a
Create Date: 2025-10-07 13:15:28.336779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1b4fbfae822b'
down_revision: Union[str, None] = '36f0b5621c0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Sync database with current models for Supabase auth integration"""
    
    # 1. Add updated_at column to profiles
    op.add_column('profiles', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    # 2. Remove description column from bands (not in current models)
    op.drop_column('bands', 'description')
    
    # 3. Update enums to uppercase values with proper casting
    
    # Create new enum types
    event_type_enum = postgresql.ENUM('REHEARSAL', 'GIG', name='eventtype')
    event_status_enum = postgresql.ENUM('PLANNED', 'CONFIRMED', 'CANCELLED', name='eventstatus')
    band_role_enum = postgresql.ENUM('LEADER', 'MEMBER', name='bandrole')
    
    # Create the new enum types
    event_type_enum.create(op.get_bind())
    event_status_enum.create(op.get_bind())
    band_role_enum.create(op.get_bind())
    
    # First, remove default values temporarily
    op.alter_column('events', 'status', server_default=None)
    op.alter_column('memberships', 'role', server_default=None)
    
    # Update events.type column with proper casting
    op.execute("ALTER TABLE events ALTER COLUMN type TYPE eventtype USING UPPER(type::text)::eventtype")
    
    # Update events.status column with proper casting  
    op.execute("ALTER TABLE events ALTER COLUMN status TYPE eventstatus USING UPPER(status::text)::eventstatus")
    
    # Update memberships.role column with proper casting
    op.execute("ALTER TABLE memberships ALTER COLUMN role TYPE bandrole USING UPPER(role::text)::bandrole")
    
    # Drop old enum types
    op.execute("DROP TYPE event_type")
    op.execute("DROP TYPE event_status") 
    op.execute("DROP TYPE band_role")
    
    # Set new default values with new enum values
    op.alter_column('events', 'status', server_default=sa.text("'PLANNED'::eventstatus"))
    op.alter_column('memberships', 'role', server_default=sa.text("'MEMBER'::bandrole"))
    
    # Drop indexes that may not exist or are not needed
    try:
        op.drop_index('idx_bands_name', table_name='bands')
    except:
        pass
    try:
        op.drop_index('idx_events_band_time', table_name='events')
    except:
        pass
    try:
        op.drop_index('idx_events_time', table_name='events')
    except:
        pass
    try:
        op.drop_index('idx_memberships_band', table_name='memberships')
    except:
        pass
    try:
        op.drop_index('idx_memberships_user', table_name='memberships')
    except:
        pass
    try:
        op.drop_index('idx_venues_band', table_name='venues')
    except:
        pass
    try:
        op.drop_constraint('memberships_band_id_user_id_key', 'memberships', type_='unique')
    except:
        pass


def downgrade() -> None:
    """Revert database changes"""
    
    # Create old enum types
    event_type_enum = postgresql.ENUM('rehearsal', 'gig', name='event_type')
    event_status_enum = postgresql.ENUM('planned', 'confirmed', 'cancelled', name='event_status')
    band_role_enum = postgresql.ENUM('leader', 'member', name='band_role')
    
    event_type_enum.create(op.get_bind())
    event_status_enum.create(op.get_bind()) 
    band_role_enum.create(op.get_bind())
    
    # Revert enum columns with proper casting
    op.execute("ALTER TABLE events ALTER COLUMN type TYPE event_type USING LOWER(type::text)::event_type")
    op.execute("ALTER TABLE events ALTER COLUMN status TYPE event_status USING LOWER(status::text)::event_status")
    op.execute("ALTER TABLE memberships ALTER COLUMN role TYPE band_role USING LOWER(role::text)::band_role")
    
    # Drop new enum types
    op.execute("DROP TYPE eventtype")
    op.execute("DROP TYPE eventstatus")
    op.execute("DROP TYPE bandrole")
    
    # Revert default values
    op.alter_column('events', 'status', server_default=sa.text("'planned'::event_status"))
    op.alter_column('memberships', 'role', server_default=sa.text("'member'::band_role"))
    
    # Add back description column
    op.add_column('bands', sa.Column('description', sa.TEXT(), nullable=True))
    
    # Remove updated_at column
    op.drop_column('profiles', 'updated_at')
