# Smart Canteen System

A Streamlit-based web application for managing a smart canteen system with real-time order tracking, stock management, and online payments.

## Features

- 🔐 Role-based authentication (Admin, Staff, Student)
- 🍽️ Real-time menu display and ordering
- 💳 Online payments with Razorpay (test mode)
- 📊 Order tracking and analytics
- 📦 Stock management with auto-reset for daily items
- 📱 Responsive UI with clean layout

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-canteen-system.git
cd smart-canteen-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Login with default credentials:
- Admin: admin / admin123
- Staff: staff / staff123
- Student: student1 / stu123

## Features by Role

### Student
- View real-time menu
- Place and track orders
- Online payment or cash on delivery
- View order history

### Canteen Staff
- View incoming orders
- Update order status
- Track completed orders

### Admin
- Manage users (add/edit/delete)
- Manage food items and stock
- View analytics and reports
- Export data to CSV

## Database

The application uses SQLite for data storage with the following tables:
- users: User authentication and role management
- food_items: Menu items and stock tracking
- orders: Order tracking and history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.