import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import json
import os
from database.db_utils import DatabaseManager
from utils.payment import PaymentManager
from components.ui import (
    display_menu, display_cart, display_order_status,
    display_order_history, display_analytics
)

# Configure Streamlit page
st.set_page_config(
    page_title="Smart Canteen System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Database initialization
def init_db():
    conn = sqlite3.connect('database/canteen.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Create food_items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            stock INTEGER NOT NULL,
            validity_type TEXT NOT NULL,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_id TEXT,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    # Insert default users if not exists
    default_users = [
        ('admin', 'admin123', 'admin'),
        ('staff', 'staff123', 'staff'),
        ('student1', 'stu123', 'student')
    ]
    
    for user in default_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                 user)
    
    conn.commit()
    conn.close()

def login():
    st.title("🍽️ Smart Canteen System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Admin", "Staff", "Student"])
        
        if st.button("Login"):
            conn = sqlite3.connect('database/canteen.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=? AND password=? AND LOWER(role)=LOWER(?)',
                     (username, password, role))
            user = c.fetchone()
            conn.close()
            
            if user:
                st.session_state.authenticated = True
                st.session_state.user_role = role.lower()
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials!")

def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.cart = []
    st.rerun()

def student_dashboard():
    st.title("Student Dashboard")
    
    # Initialize database and payment managers
    db = DatabaseManager()
    payment = PaymentManager()
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        if st.button("Logout"):
            logout()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Order Food", "Active Orders", "Order History"])
    
    with tab1:
        st.subheader("Available Menu")
        
        # Display menu
        menu_items = db.get_menu_items()
        
        def add_to_cart(item, quantity):
            cart_item = {
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': quantity
            }
            st.session_state.cart.append(cart_item)
            st.success(f"Added {quantity} x {item['name']} to cart")
        
        display_menu(menu_items, add_to_cart)
        
        # Display cart
        st.markdown("---")
        
        def remove_from_cart(item):
            st.session_state.cart.remove(item)
        
        total = display_cart(st.session_state.cart, remove_from_cart)
        
        if st.session_state.cart:
            payment_method = st.radio(
                "Payment Method",
                ["Cash on Delivery", "Razorpay"]
            )
            
            if st.button("Place Order"):
                if payment_method == "Razorpay":
                    payment_response = payment.process_payment(total)
                    if payment_response['status'] == 'success':
                        order_id = db.create_order(
                            st.session_state.username,
                            st.session_state.cart,
                            total,
                            'razorpay',
                            payment_response['payment_id']
                        )
                else:
                    order_id = db.create_order(
                        st.session_state.username,
                        st.session_state.cart,
                        total,
                        'cod'
                    )
                
                # Update stock
                for item in st.session_state.cart:
                    db.update_stock(item['id'], item['quantity'])
                
                st.session_state.cart = []
                st.success(f"Order placed successfully! Order ID: {order_id}")
                st.rerun()
    
    with tab2:
        st.subheader("Active Orders")
        active_orders = db.get_user_orders(st.session_state.username)
        active_orders = active_orders[active_orders['status'] != 'prepared']
        
        if not active_orders.empty:
            for _, order in active_orders.iterrows():
                display_order_status(order['order_id'], order['status'])
        else:
            st.info("No active orders")
    
    with tab3:
        st.subheader("Order History")
        orders = db.get_user_orders(st.session_state.username)
        display_order_history(orders)

def staff_dashboard():
    st.title("Staff Dashboard")
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        if st.button("Logout"):
            logout()
    
    # Main content
    st.subheader("Incoming Orders")
    
    # Get all orders that are not completed
    orders = db.get_all_orders()
    active_orders = orders[orders['status'] != 'prepared']
    
    if active_orders.empty:
        st.info("No active orders")
    else:
        for _, order in active_orders.iterrows():
            with st.expander(f"Order #{order['order_id']} - {order['timestamp']}"):
                st.write(f"**Customer:** {order['username']}")
                st.write(f"**Payment:** {order['payment_method']}")
                st.write(f"**Amount:** ₹{order['total_amount']:.2f}")
                
                # Display items
                items = pd.read_json(order['items'])
                st.write("**Items:**")
                for _, item in items.iterrows():
                    st.write(f"- {item['quantity']}x {item['name']}")
                
                # Status update buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if order['status'] != 'placed' and st.button('Mark as Placed', key=f"placed_{order['order_id']}"):
                        db.update_order_status(order['order_id'], 'placed')
                        st.rerun()
                
                with col2:
                    if order['status'] != 'preparing' and st.button('Mark as Preparing', key=f"preparing_{order['order_id']}"):
                        db.update_order_status(order['order_id'], 'preparing')
                        st.rerun()
                
                with col3:
                    if order['status'] != 'prepared' and st.button('Mark as Prepared', key=f"prepared_{order['order_id']}"):
                        db.update_order_status(order['order_id'], 'prepared')
                        st.rerun()
    
    # Completed orders
    st.markdown("---")
    st.subheader("Completed Orders")
    completed_orders = orders[orders['status'] == 'prepared']
    
    if completed_orders.empty:
        st.info("No completed orders")
    else:
        for _, order in completed_orders.iterrows():
            with st.expander(f"Order #{order['order_id']} - {order['timestamp']}"):
                st.write(f"**Customer:** {order['username']}")
                st.write(f"**Payment:** {order['payment_method']}")
                st.write(f"**Amount:** ₹{order['total_amount']:.2f}")
                items = pd.read_json(order['items'])
                st.write("**Items:**")
                for _, item in items.iterrows():
                    st.write(f"- {item['quantity']}x {item['name']}")

def admin_dashboard():
    st.title("Admin Dashboard")
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        if st.button("Logout"):
            logout()
    
    # Main content tabs
    tabs = st.tabs(["User Management", "Food Items", "Analytics"])
    
    with tabs[0]:
        st.subheader("User Management")
        
        # Add new user
        with st.expander("Add New User"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["admin", "staff", "student"])
            
            if st.button("Add User"):
                conn = sqlite3.connect('database/canteen.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                            (new_username, new_password, new_role))
                    conn.commit()
                    st.success("User added successfully!")
                except sqlite3.IntegrityError:
                    st.error("Username already exists!")
                conn.close()
                st.rerun()
        
        # List and manage users
        conn = sqlite3.connect('database/canteen.db')
        users = pd.read_sql_query('SELECT * FROM users', conn)
        conn.close()
        
        st.write("### Current Users")
        for _, user in users.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{user['username']}** ({user['role']})")
            
            with col2:
                if st.button("Reset Password", key=f"reset_{user['username']}"):
                    conn = sqlite3.connect('database/canteen.db')
                    c = conn.cursor()
                    c.execute('UPDATE users SET password = ? WHERE username = ?',
                            ('password123', user['username']))
                    conn.commit()
                    conn.close()
                    st.success(f"Password reset for {user['username']}")
            
            with col3:
                if user['username'] not in ['admin', 'staff', 'student1']:
                    if st.button("Delete", key=f"delete_{user['username']}"):
                        conn = sqlite3.connect('database/canteen.db')
                        c = conn.cursor()
                        c.execute('DELETE FROM users WHERE username = ?',
                                (user['username'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
    
    with tabs[1]:
        st.subheader("Food Items Management")
        
        # Add new food item
        with st.expander("Add New Food Item"):
            name = st.text_input("Item Name")
            price = st.number_input("Price (₹)", min_value=0.0, step=0.5)
            category = st.selectbox("Category", ["Breakfast", "Lunch", "Snacks", "Beverages"])
            stock = st.number_input("Initial Stock", min_value=0)
            validity_type = st.selectbox("Validity Type", ["daily", "regular"])
            
            if st.button("Add Item"):
                db.add_food_item(name, price, category, stock, validity_type)
                st.success("Item added successfully!")
                st.rerun()
        
        # List and manage food items
        menu_items = db.get_menu_items()
        
        st.write("### Current Menu Items")
        for _, item in menu_items.iterrows():
            with st.expander(f"{item['name']} ({item['category']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Price:** ₹{item['price']:.2f}")
                    st.write(f"**Stock:** {item['stock']}")
                    st.write(f"**Type:** {item['validity_type']}")
                
                with col2:
                    new_stock = st.number_input("Update Stock",
                                              min_value=0,
                                              value=item['stock'],
                                              key=f"stock_{item['id']}")
                    
                    if st.button("Update Stock", key=f"update_{item['id']}"):
                        db.update_food_item(
                            item['id'],
                            item['name'],
                            item['price'],
                            item['category'],
                            new_stock,
                            item['validity_type']
                        )
                        st.success("Stock updated!")
                        st.rerun()
                    
                    if st.button("Delete Item", key=f"delete_item_{item['id']}"):
                        db.delete_food_item(item['id'])
                        st.success("Item deleted!")
                        st.rerun()
        
        # Reset daily items
        st.markdown("---")
        if st.button("Reset Daily Items"):
            db.reset_daily_items()
            st.success("Daily items reset successfully!")
            st.rerun()
    
    with tabs[2]:
        st.subheader("Order Analytics")
        
        analytics = db.get_analytics()
        
        # Display analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Orders", analytics['total_orders'])
            
            st.write("### Payment Methods")
            payment_stats = analytics['payment_stats']
            if not payment_stats.empty:
                st.bar_chart(payment_stats.set_index('payment_method'))
        
        with col2:
            st.write("### Most Sold Items")
            most_sold = analytics['most_sold']
            if not most_sold.empty:
                st.bar_chart(most_sold.set_index('items'))
        
        # Export data
        if st.button("Export Orders CSV"):
            orders = db.get_all_orders()
            orders.to_csv('orders_export.csv', index=False)
            st.success("Orders exported to orders_export.csv")

def main():
    # Initialize database
    if not os.path.exists('database'):
        os.makedirs('database')
    init_db()
    
    # Main application logic
    if not st.session_state.authenticated:
        login()
    else:
        if st.session_state.user_role == 'student':
            student_dashboard()
        elif st.session_state.user_role == 'staff':
            staff_dashboard()
        elif st.session_state.user_role == 'admin':
            admin_dashboard()

if __name__ == "__main__":
    main()






