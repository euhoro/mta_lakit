import sqlite3

from atm_repository import InventoryService


class SQLiteInventoryService(InventoryService):
    def __init__(self, db_path='inventory.db'):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    type TEXT NOT NULL,
                    denomination REAL NOT NULL,
                    amount INTEGER NOT NULL,
                    PRIMARY KEY (type, denomination)
                )
            ''')
            # Initial inventory setup
            cursor.execute('SELECT COUNT(*) FROM inventory')
            if cursor.fetchone()[0] == 0:
                initial_inventory = {
                    "BILL": {200: 7, 100: 4, 20: 15},
                    "COIN": {10: 10, 1: 10, 5: 1, 0.1: 12, 0.01: 21}
                }
                for type, denominations in initial_inventory.items():
                    for denomination, amount in denominations.items():
                        cursor.execute('''
                            INSERT INTO inventory (type, denomination, amount)
                            VALUES (?, ?, ?)
                        ''', (type, denomination, amount))
            conn.commit()

    def read_inventory(self):
        inventory = {"BILL": {}, "COIN": {}}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT type, denomination, amount FROM inventory')
            rows = cursor.fetchall()
            for type, denomination, amount in rows:
                inventory[type][denomination] = amount
        return inventory

    def write_inventory(self, inventory):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for type, denominations in inventory.items():
                for denomination, amount in denominations.items():
                    cursor.execute('''
                        UPDATE inventory
                        SET amount = ?
                        WHERE type = ? AND denomination = ?
                    ''', (amount, type, denomination))
            conn.commit()
