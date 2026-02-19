from datetime import datetime, timezone
from typing import Optional
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
    
    # Default display map
    primary_map: so.Mapped[Optional['Map']] = so.relationship(
        foreign_keys=[primary_map_id],
        post_update=True
    )

    # All associated maps
    maps: so.Mapped[list['Map']] = so.relationship(
        'Map',
        foreign_keys='Map.world_id',
        back_populates='world',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'{self.name}:{self.info}'

    
class Map(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    world: so.Mapped['World'] = so.relationship(
        'World',
        foreign_keys=[id],
        back_populates='maps'
    )
    
    pins: so.Mapped[list['Pin']] = so.relationship(
        'Pin',
        foreign_keys='Pin.map_id',
        back_populates='map',
        cascade='all, delete-orphan'
    )
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    body_path: so.Mapped[str] = so.mapped_column(sa.String(255))
    added: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    
    connected_maps: so.Mapped[list['Map']] = so.relationship(
        'Map',
        secondary='map_connections',
        primaryjoin='Map.id==map_connections.c.map_id',
        secondaryjoin='Map.id==map_connections.c.connected_map_id',
        backref='connected_from'
    )

    def __repr__(self):
        return f'Map {self.id} for world {self.world_id}'

class Pin(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    map_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('map.id', name='fk_pin_map', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Position as percentages (0-100) for responsive scaling
    x_percent: so.Mapped[float] = so.mapped_column(
        sa.Numeric(5, 2),
        nullable=False
    )
    y_percent: so.Mapped[float] = so.mapped_column(
        sa.Numeric(5, 2),
        nullable=False
    )

    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    color: so.Mapped[str] = so.mapped_column(
        sa.String(7),
        default='#b89fda'
    )
    
    target_map_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('map.id', name='fk_pin_target_map', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    added: so.Mapped[datetime] = so.mapped_column(
        index=True,
        default=lambda: datetime.now(timezone.utc)
    )
    
    host_map: so.Mapped['Map'] = so.relationship(
        'Map',
        foreign_keys=[map_id],
        back_populates='pins'
    )
    
    target_map: so.Mapped[Optional['Map']] = so.relationship(
        'Map',
        foreign_keys=[target_map_id]
    )
    
    def __repr__(self):
        link_info = f" → map_id={self.target_map_id}" if self.target_map_id else ""
        return f'<Pin id={self.id} name="{self.name or "Unnamed"}" map_id={self.map_id}{link_info}>'


map_connections = sa.Table(
    'map_connections',
    db.Model.metadata,
    sa.Column('map_id', sa.Integer, sa.ForeignKey('map.id'), primary_key=True),
    sa.Column('connected_map_id', sa.Integer, sa.ForeignKey('map.id'), primary_key=True)
)