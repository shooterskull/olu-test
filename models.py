# Author: Lee Shen Juin
from app import db

class Shop(db.Model):
    __tablename__ = "shops"
 
    unit = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    mall = db.Column(db.String(20), nullable=False)
    imageurl = db.Column(db.String, nullable=False)
 
    def __init__(self, unit, name, mall, imageurl):
        self.unit = unit
        self.name = name
        self.mall = mall
        self.imageurl = imageurl
 
    def __repr__(self):
        return '<Name {}>'.format(self.name)
