from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class World(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    thumbnail_path: so.Mapped[str] = so.mapped_column(sa.String(255), default='./static/images/default.png')
    created: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    maps: so.WriteOnlyMapped['Map'] = so.relationship(back_populates='world')

    def __repr__(self):
        return f'{self.name}'
    
class Map(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    world_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(World.id), index=True)
    body_path: so.Mapped[str] = so.mapped_column(sa.String(255))
    added: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    world: so.Mapped[World] = so.relationship(back_populates='maps')
