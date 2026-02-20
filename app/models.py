from datetime import datetime, timezone
from typing import List, Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class World(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    thumbnail_path: so.Mapped[str] = so.mapped_column(sa.String(255), default='images/default.png')
    created: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    info: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    primary_map_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('map.id', name='fk_world_primary_map'), 
        nullable=True
    )
    
    primary_map: so.Mapped[Optional['Map']] = so.relationship(
        foreign_keys=[primary_map_id],
        post_update=True,
        overlaps='maps'  # Tell SQLAlchemy this is okay
    )

    maps: so.Mapped[list['Map']] = so.relationship(
        'Map',
        foreign_keys='[Map.world_id]',  # Note the brackets!
        back_populates='world',
        cascade='all, delete-orphan',
        overlaps='primary_map'  # Tell SQLAlchemy this is okay
    )

    def __repr__(self):
        return f'{self.name}:{self.info}'

    
class Map(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    world_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('world.id', name='fk_map_world'), 
        index=True
    )
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    body_path: so.Mapped[str] = so.mapped_column(sa.String(255))
    added: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    world: so.Mapped['World'] = so.relationship(
        'World',
        foreign_keys=[world_id],
        back_populates='maps'
    )
    
    connected_maps: so.Mapped[list['Map']] = so.relationship(
        'Map',
        secondary='map_connections',
        primaryjoin='Map.id==map_connections.c.map_id',
        secondaryjoin='Map.id==map_connections.c.connected_map_id',
        backref='connected_from'
    )


map_connections = sa.Table(
    'map_connections',
    db.Model.metadata,
    sa.Column('map_id', sa.Integer, sa.ForeignKey('map.id'), primary_key=True),
    sa.Column('connected_map_id', sa.Integer, sa.ForeignKey('map.id'), primary_key=True)
)