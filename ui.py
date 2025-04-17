import streamlit as st
import pandas as pd
from datetime import datetime

def display_menu(menu_items, on_add_to_cart):
    """Display food menu with add to cart functionality"""
    for _, item in menu_items.iterrows():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{item['name']}** ({item['category']})")
        
        with col2:
            st.write(f"₹{item['price']:.2f}")
        
        with col3:
            st.write(f"Stock: {item['stock']}")
        
        with col4:
            quantity = st.number_input(
                "Qty",
                min_value=0,
                max_value=item['stock'],
                value=0,
                key=f"qty_{item['id']}"
            )
            if quantity > 0:
                if st.button("Add", key=f"add_{item['id']}"):
                    on_add_to_cart(item, quantity)

def display_cart(cart_items, on_remove):
    """Display shopping cart"""
    if not cart_items:
        st.info("Your cart is empty")
        return
    
    st.write("### Your Cart")
    total = 0
    
    for item in cart_items:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(item['name'])
        
        with col2:
            st.write(f"₹{item['price']:.2f}")
        
        with col3:
            st.write(f"x{item['quantity']}")
        
        with col4:
            if st.button("Remove", key=f"remove_{item['id']}"):
                on_remove(item)
        
        total += item['price'] * item['quantity']
    
    st.write(f"**Total: ₹{total:.2f}**")
    return total

def display_order_status(order_id, status):
    """Display order status with color coding"""
    status_colors = {
        'placed': '🟡',
        'preparing': '🟠',
        'prepared': '🟢'
    }
    
    status_messages = {
        'placed': 'Order placed successfully',
        'preparing': 'Your order is being prepared...',
        'prepared': 'Your order is ready! Please collect it.'
    }
    
    st.write(f"### Order #{order_id}")
    st.write(f"{status_colors.get(status, '⚪')} Status: {status.title()}")
    st.info(status_messages.get(status, 'Status unknown'))

def display_order_history(orders):
    """Display order history in a table"""
    if orders.empty:
        st.info("No orders found")
        return
    
    for _, order in orders.iterrows():
        with st.expander(f"Order #{order['order_id']} - {order['timestamp']}"):
            st.write(f"**Status:** {order['status'].title()}")
            st.write(f"**Payment:** {order['payment_method']}")
            st.write(f"**Amount:** ₹{order['total_amount']:.2f}")
            st.write("**Items:**")
            items = pd.read_json(order['items'])
            st.dataframe(items[['name', 'quantity', 'price']])

def display_analytics(analytics_data):
    """Display analytics dashboard"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Orders", analytics_data['total_orders'])
        
        st.write("### Payment Methods")
        st.bar_chart(analytics_data['payment_stats'].set_index('payment_method'))
    
    with col2:
        st.write("### Most Sold Items")
        st.bar_chart(analytics_data['most_sold'].set_index('items'))