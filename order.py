from database import DB
from comment import Comment


class Order:
    def __init__(self, id, name, description, price, date_added, active, buyer_id = None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.date_added = date_added
        self.active = active
        self.buyer_id = buyer_id

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM orders').fetchall()
            return [Order(*row) for row in rows]

    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute(
                'SELECT * FROM orders WHERE id = ?',
                (id,)
            ).fetchone()
            return Order(*row)

    def create(self):
        with DB() as db:
            values = (self.name, self.description, self.price, self.date_added, self.active, self.buyer_id)
            db.execute('''
                INSERT INTO posts (name, description, price, date_added, active, buyer_id)
                VALUES (?, ?, ?, ?, ?, ?)''', values)
            return self

    def save(self):
        with DB() as db:
            values = (
                self.name,
                self.description,
                self.price,
                self.date_added,
                self.active,
                self.buyer_id
                self.id
            )
            db.execute(
                '''UPDATE posts
                SET name = ?, description = ?, price = ?, date_added = ?, active = ?, buyer_id = ?
                WHERE id = ?''', values)
            return self

    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM posts WHERE id = ?', (self.id,))

