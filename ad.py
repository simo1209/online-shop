from database import DB
from errors import ApplicationError


class Ad:
    def __init__(self, id, name, description, price, date_added, creator_id, active = 1, buyer_id = 0):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.date_added = date_added
        self.active = active
        self.buyer_id = buyer_id
        self.creator_id = creator_id

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM ads').fetchall()
            return [Ad(*row) for row in rows]

    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute(
                'SELECT * FROM ads WHERE id = ?',
                (id,)
            ).fetchone()
            if row is None:
                raise ApplicationError("Ad doesnt exist", 404)
            return Ad(*row)

    def create(self):
        with DB() as db:
            values = (self.name, self.description, self.price, self.creator_id, self.active, self.buyer_id)
            db.execute('''
                INSERT INTO ads (name, description, price, creator_id, date_added, active, buyer_id)
                VALUES (?, ?, ?, ?, date('now'), ?, ?)''', values)
            return self

    def save(self):
        with DB() as db:
            values = (
                self.name,
                self.description,
                self.price,
                self.active,
                self.buyer_id,
                self.id
            )
            db.execute(
                '''UPDATE ads
                SET name = ?, description = ?, price = ?, active = ?, buyer_id = ?
                WHERE id = ?''', values)
            return self

    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM ads WHERE id = ?', (self.id,))

