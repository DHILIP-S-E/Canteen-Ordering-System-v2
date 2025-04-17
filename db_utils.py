import sqlite3
import pandas as pd
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_path='database/canteen.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_menu_items(self):
        conn = self.get_connection()
        query = '''
            SELECT * FROM food_items 
            WHERE active = 1 AND (stock > 0 OR validity_type = 'daily')
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_stock(self, item_id, quantity):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE food_items 
            SET stock = stock - ? 
            WHERE id = ? AND validity_type != 'daily'
        ''', (quantity, item_id))
        conn.commit()
        conn.close()
    
    def create_order(self, username, items, total_amount, payment_method, payment_id=None):
        conn = self.get_connection()
        c = conn.cursor()
        
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        items_json = json.dumps(items)
        
        c.execute('''
            INSERT INTO orders (order_id, username, items, total_amount, 
                              payment_method, payment_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'placed')
        ''', (order_id, username, items_json, total_amount, payment_method, payment_id))
        
        conn.commit()
        conn.close()
        return order_id
    
    def get_user_orders(self, username):
        conn = self.get_connection()
        query = '''
            SELECT * FROM orders 
            WHERE username = ? 
            ORDER BY timestamp DESC
        '''
        df = pd.read_sql_query(query, conn, params=[username])
        conn.close()
        return df
    
    def get_all_orders(self, status=None):
        conn = self.get_connection()
        if status:
            query = 'SELECT * FROM orders WHERE status = ? ORDER BY timestamp DESC'
            df = pd.read_sql_query(query, conn, params=[status])
        else:
            query = 'SELECT * FROM orders ORDER BY timestamp DESC'
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_order_status(self, order_id, status):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE orders SET status = ? WHERE order_id = ?',
                 (status, order_id))
        conn.commit()
        conn.close()
    
    def add_food_item(self, name, price, category, stock, validity_type):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO food_items (name, price, category, stock, validity_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, price, category, stock, validity_type))
        conn.commit()
        conn.close()
    
    def update_food_item(self, item_id, name, price, category, stock, validity_type):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE food_items 
            SET name = ?, price = ?, category = ?, stock = ?, validity_type = ?
            WHERE id = ?
        ''', (name, price, category, stock, validity_type, item_id))
        conn.commit()
        conn.close()
    
    def delete_food_item(self, item_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE food_items SET active = 0 WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
    
    def reset_daily_items(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE food_items SET stock = 0 WHERE validity_type = 'daily'")
        conn.commit()
        conn.close()
    
    def get_analytics(self):
        conn = self.get_connection()
        
        # Total orders
        total_orders = pd.read_sql_query(
            'SELECT COUNT(*) as total FROM orders', conn).iloc[0]['total']
        
        # Payment method stats
        payment_stats = pd.read_sql_query('''
            SELECT payment_method, COUNT(*) as count 
            FROM orders GROUP BY payment_method
        ''', conn)
        
        # Most sold items
        most_sold = pd.read_sql_query('''
            SELECT items, COUNT(*) as count 
            FROM orders GROUP BY items 
            ORDER BY count DESC LIMIT 5
        ''', conn)
        
        conn.close()
        
        return {
            'total_orders': total_orders,
            'payment_stats': payment_stats,
            'most_sold': most_sold
        }