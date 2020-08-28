from virtual_hospital import db


class BlankEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_attribute = db.Column(db.String(32))
