from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class World(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    icon_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255), index=True)

    def __repr__(self):
        return f'{self.name}'