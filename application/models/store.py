from db import db


class Store(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    items = db.relationship(
        "ItemModel", back_populates="store", lazy="dynamic"
    )
