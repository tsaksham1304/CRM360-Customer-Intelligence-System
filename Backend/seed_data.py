"""
CRM 360 — Database Seeder
Run this ONCE to populate your MySQL database with realistic sample data.
Usage: python seed_data.py
"""

import random
from datetime import datetime, timedelta
from db import get_connection

# ============================================================
#  REALISTIC INDIAN DATA
# ============================================================

FIRST_NAMES_M = ['Rahul', 'Amit', 'Vikram', 'Rohan', 'Karan', 'Arjun', 'Suresh', 'Rajesh', 'Anil', 'Sanjay',
                 'Deepak', 'Manish', 'Nikhil', 'Gaurav', 'Pankaj', 'Vivek', 'Ashish', 'Mohit', 'Sachin', 'Vishal',
                 'Ravi', 'Ajay', 'Naveen', 'Harish', 'Dinesh', 'Pranav', 'Kunal', 'Tarun', 'Varun', 'Akash',
                 'Abhishek', 'Siddharth', 'Aarav', 'Dev', 'Ishaan', 'Yash', 'Kartik', 'Anand', 'Bharat', 'Chirag']

FIRST_NAMES_F = ['Priya', 'Sneha', 'Ananya', 'Neha', 'Meera', 'Kavita', 'Pooja', 'Ritu', 'Swati', 'Divya',
                 'Nisha', 'Asha', 'Lakshmi', 'Geeta', 'Sunita', 'Anjali', 'Pallavi', 'Shruti', 'Tanvi', 'Isha',
                 'Aishwarya', 'Bhavna', 'Chitra', 'Disha', 'Esha', 'Falguni', 'Gauri', 'Hema', 'Jaya', 'Kritika',
                 'Lavanya', 'Madhuri', 'Nandini', 'Payal', 'Radhika', 'Sonal', 'Tara', 'Uma', 'Varsha', 'Yamini']

LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Reddy', 'Nair', 'Joshi', 'Malhotra',
              'Kapoor', 'Das', 'Iyer', 'Mehta', 'Agarwal', 'Bhat', 'Chauhan', 'Desai', 'Ghosh', 'Hegde',
              'Jain', 'Kulkarni', 'Mishra', 'Pandey', 'Rao', 'Saxena', 'Thakur', 'Yadav', 'Pillai', 'Banerjee',
              'Srivastava', 'Tiwari', 'Dubey', 'Bhatt', 'Choudhury', 'Dutta', 'Menon', 'Mukherjee', 'Sethi', 'Bose']

CITIES = [
    ('Mumbai', 'Maharashtra', '400001'), ('Delhi', 'Delhi', '110001'), ('Bangalore', 'Karnataka', '560001'),
    ('Chennai', 'Tamil Nadu', '600001'), ('Hyderabad', 'Telangana', '500001'), ('Pune', 'Maharashtra', '411001'),
    ('Kolkata', 'West Bengal', '700001'), ('Ahmedabad', 'Gujarat', '380001'), ('Jaipur', 'Rajasthan', '302001'),
    ('Lucknow', 'Uttar Pradesh', '226001'), ('Chandigarh', 'Chandigarh', '160001'), ('Indore', 'Madhya Pradesh', '452001'),
    ('Bhopal', 'Madhya Pradesh', '462001'), ('Nagpur', 'Maharashtra', '440001'), ('Coimbatore', 'Tamil Nadu', '641001'),
    ('Kochi', 'Kerala', '682001'), ('Vadodara', 'Gujarat', '390001'), ('Surat', 'Gujarat', '395001'),
    ('Noida', 'Uttar Pradesh', '201301'), ('Gurgaon', 'Haryana', '122001'), ('Visakhapatnam', 'Andhra Pradesh', '530001'),
    ('Patna', 'Bihar', '800001'), ('Bhubaneswar', 'Odisha', '751001'), ('Mysuru', 'Karnataka', '570001'),
    ('Thiruvananthapuram', 'Kerala', '695001'), ('Dehradun', 'Uttarakhand', '248001')
]

PRODUCTS = [
    ('Laptop', 55000, 45), ('Gaming Laptop', 85000, 20), ('Ultrabook', 72000, 30),
    ('Smartphone', 22000, 120), ('Premium Phone', 45000, 60), ('Budget Phone', 12000, 200),
    ('Wireless Earbuds', 3500, 300), ('Over-Ear Headphones', 6000, 150), ('Neckband', 1500, 250),
    ('Mechanical Keyboard', 4500, 100), ('Wireless Keyboard', 2000, 180), ('Gaming Mouse', 2500, 200),
    ('Wireless Mouse', 1200, 250), ('Smartwatch', 8000, 90), ('Fitness Band', 3000, 180),
    ('Tablet', 28000, 50), ('iPad', 42000, 35), ('Monitor 24"', 14000, 60),
    ('Monitor 27"', 22000, 40), ('Webcam HD', 3500, 120), ('USB-C Hub', 2500, 200),
    ('Power Bank', 1800, 300), ('Bluetooth Speaker', 4000, 150), ('Soundbar', 12000, 45),
    ('Printer', 8000, 30), ('SSD 500GB', 4500, 100), ('External HDD', 5000, 80),
    ('Router', 3000, 90), ('Smart Plug', 800, 400), ('Desk Lamp', 2000, 150)
]

ISSUE_TYPES = ['Payment Issue', 'Delivery Delay', 'Product Defect', 'Wrong Item Received', 'Refund Request',
               'Login Issue', 'Account Problem', 'Order Cancellation', 'Return Request', 'Billing Error',
               'App Crash', 'Warranty Claim', 'Size/Color Exchange', 'Missing Item', 'Damaged Package']

ISSUE_DESCS = {
    'Payment Issue': ['Amount deducted but order not confirmed', 'Double charged for single order', 'Payment failed but money debited', 'UPI payment stuck in processing'],
    'Delivery Delay': ['Order delayed by 5 days', 'No tracking update since 3 days', 'Delivery partner not responding', 'Package stuck at warehouse'],
    'Product Defect': ['Screen has dead pixels', 'Battery draining fast', 'Speaker not working', 'Device overheating'],
    'Wrong Item Received': ['Received different color', 'Wrong model delivered', 'Received someone else order', 'Quantity mismatch'],
    'Refund Request': ['Refund not credited yet', 'Partial refund received', 'Want refund instead of replacement', 'Refund pending for 10 days'],
    'Login Issue': ['Unable to login to account', 'OTP not received', 'Password reset not working', 'Account locked'],
    'Account Problem': ['Cannot update profile', 'Address not saving', 'Phone number change needed', 'Email verification failed'],
    'Order Cancellation': ['Want to cancel before shipping', 'Ordered by mistake', 'Found better price elsewhere', 'Delivery date too far'],
    'Return Request': ['Product not as described', 'Changed my mind', 'Better option available', 'Product too heavy'],
    'Billing Error': ['Invoice amount incorrect', 'GST not applied correctly', 'Discount code not applied', 'Membership charge incorrect'],
    'App Crash': ['App crashes on payment page', 'Cannot open order history', 'Cart items disappearing', 'Search not working'],
    'Warranty Claim': ['Product stopped working after 3 months', 'Want warranty replacement', 'Warranty card missing', 'Claim rejected incorrectly'],
    'Size/Color Exchange': ['Need different size', 'Color not as shown', 'Want to exchange for another variant', 'Size chart was wrong'],
    'Missing Item': ['One item missing from order', 'Accessory not included', 'Charger missing from box', 'Manual not in package'],
    'Damaged Package': ['Box was crushed', 'Water damage on package', 'Product scratched inside', 'Seal broken on delivery']
}

FEEDBACK_COMMENTS = {
    5: ['Excellent service! Highly recommended', 'Best CRM experience ever', 'Super fast delivery, great quality',
        'Amazing product, exceeded expectations', 'Outstanding customer support', 'Will definitely buy again',
        'Premium quality, worth every rupee', 'Flawless experience from start to finish'],
    4: ['Good experience overall', 'Nice product, minor improvements needed', 'Delivery was quick, packaging could be better',
        'Satisfied with the purchase', 'Good value for money', 'Happy with the service', 'Smooth checkout process'],
    3: ['Average experience', 'Product is okay, nothing special', 'Delivery took longer than expected',
        'Customer support was slow', 'Product quality is decent', 'Could be better for the price'],
    2: ['Below expectations', 'Product quality not great', 'Delivery was delayed significantly',
        'Support team was unhelpful', 'Would not recommend', 'Disappointing experience'],
    1: ['Terrible experience', 'Product arrived damaged', 'Worst customer service ever',
        'Complete waste of money', 'Never buying again', 'Extremely dissatisfied']
}

CALL_PURPOSES = ['Order status inquiry', 'Delivery tracking', 'Payment issue', 'Refund status', 'Product information',
                 'Return pickup inquiry', 'Account update', 'Complaint follow-up', 'Warranty inquiry', 'Bulk order inquiry',
                 'Subscription renewal', 'Address change request', 'Offer/discount inquiry', 'Technical support',
                 'Feedback follow-up', 'Membership upgrade']

PAGES_VISITED = ['Homepage', 'Product Catalog', 'Product Page', 'Cart Page', 'Checkout Page', 'Payment Page',
                 'Order Tracking', 'Profile Page', 'Wishlist', 'Offers Page', 'Help Center', 'Contact Us',
                 'Return Policy', 'Blog', 'About Us', 'Login Page', 'Signup Page', 'Search Results',
                 'Category - Electronics', 'Category - Accessories', 'Review Page', 'Compare Products']

AGENT_NAMES = [
    ('Arjun Mehta', 'arjun@crm.com', '8888000011', 'Technical'),
    ('Priya Nair', 'priya.n@crm.com', '8888000022', 'Customer Service'),
    ('Ritika Sharma', 'ritika@crm.com', '8888000033', 'Order Support'),
    ('Manoj Kumar', 'manoj@crm.com', '8888000044', 'Returns'),
    ('Snehal Desai', 'snehal@crm.com', '8888000055', 'Billing'),
    ('Rahul Saxena', 'rahul.s@crm.com', '8888000066', 'Technical'),
    ('Ankita Jain', 'ankita@crm.com', '8888000077', 'Customer Service'),
    ('Vijay Thakur', 'vijay@crm.com', '8888000088', 'Order Support')
]

PAYMENT_METHODS = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash on Delivery', 'EMI', 'Wallet']
ORDER_STATUSES = ['Delivered', 'Delivered', 'Delivered', 'Delivered', 'Shipped', 'Shipped', 'Processing', 'Cancelled']
TICKET_STATUSES = ['Open', 'Resolved', 'Resolved', 'Resolved', 'Closed', 'Closed']
INTERACTION_TYPES = ['Page View', 'Page View', 'Page View', 'Click', 'Click', 'Form Submit', 'Search', 'Add to Cart']


def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    return start_date + timedelta(days=random_days, seconds=random_seconds)


def random_ip():
    return f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"


def seed():
    conn = get_connection()
    cursor = conn.cursor()

    print("[1/8] Clearing old data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in ['web_interaction', 'call_log', 'feedback', 'support_ticket', 'support_agent',
                   'order_details', 'orders', 'products', 'customer', 'customer_segment']:
        cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    # ==================== SEGMENTS ====================
    print("[2/8] Inserting customer segments...")

    segments = [(1, 'Premium', 'High-value loyal customers', '2025-01-01'),
                (2, 'Regular', 'Moderate frequency buyers', '2025-01-01'),
                (3, 'New', 'Recently joined customers', '2025-06-01')]
    cursor.executemany("INSERT INTO customer_segment VALUES (%s,%s,%s,%s)", segments)

    # ==================== PRODUCTS ====================
    print("[3/8] Inserting products...")
    products = [(200 + i, p[0], p[1], p[2]) for i, p in enumerate(PRODUCTS)]
    cursor.executemany("INSERT INTO products VALUES (%s,%s,%s,%s)", products)
    product_ids = [p[0] for p in products]
    product_prices = {p[0]: p[2] for p in products}

    # ==================== CUSTOMERS (150) ====================
    print("[4/8] Inserting 150 customers...")
    customers = []
    emails_used = set()
    for i in range(150):
        cid = 1001 + i
        gender = random.choice(['Male', 'Female'])
        first = random.choice(FIRST_NAMES_M if gender == 'Male' else FIRST_NAMES_F)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"

        base_email = f"{first.lower()}.{last.lower()}"
        email = f"{base_email}@gmail.com"
        counter = 1
        while email in emails_used:
            email = f"{base_email}{counter}@gmail.com"
            counter += 1
        emails_used.add(email)

        phone = f"9{random.randint(100000000, 999999999)}"
        dob = random_date(datetime(1985, 1, 1), datetime(2003, 12, 31)).strftime('%Y-%m-%d')
        city, state, pincode = random.choice(CITIES)
        segment = random.choices([1, 2, 3], weights=[25, 50, 25])[0]
        customers.append((cid, name, email, phone, gender, dob, city, state, pincode, segment))

    cursor.executemany("INSERT INTO customer VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", customers)
    customer_ids = [c[0] for c in customers]

    # ==================== AGENTS (8) ====================
    print("[4b] Inserting support agents...")
    agents = [(401 + i, a[0], a[1], a[2], a[3]) for i, a in enumerate(AGENT_NAMES)]
    cursor.executemany("INSERT INTO support_agent VALUES (%s,%s,%s,%s,%s)", agents)
    agent_ids = [a[0] for a in agents]

    # ==================== ORDERS (400) ====================
    print("[5/8] Inserting 400 orders...")
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2026, 4, 20)
    orders = []
    order_details_list = []

    for i in range(400):
        oid = 3001 + i
        cid = random.choice(customer_ids)
        odate = random_date(start_date, end_date)
        payment = random.choice(PAYMENT_METHODS)
        status = random.choice(ORDER_STATUSES)

        # Generate 1-4 items per order
        num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 18, 7])[0]
        selected_products = random.sample(product_ids, min(num_items, len(product_ids)))
        total = 0

        for pid in selected_products:
            qty = random.randint(1, 3)
            price = product_prices[pid] * qty
            total += price
            order_details_list.append((oid, pid, qty, price))

        orders.append((oid, cid, odate.strftime('%Y-%m-%d %H:%M:%S'), total, payment, status))

    cursor.executemany("INSERT INTO orders VALUES (%s,%s,%s,%s,%s,%s)", orders)
    cursor.executemany("INSERT INTO order_details VALUES (%s,%s,%s,%s)", order_details_list)

    # ==================== SUPPORT TICKETS (120) ====================
    print("[6/8] Inserting 120 support tickets...")
    tickets = []
    for i in range(120):
        tid = 5001 + i
        cid = random.choice(customer_ids)
        aid = random.choice(agent_ids)
        issue_type = random.choice(ISSUE_TYPES)
        issue_desc = random.choice(ISSUE_DESCS[issue_type])
        status = random.choice(TICKET_STATUSES)
        created = random_date(start_date, end_date)
        resolved = None
        if status in ('Resolved', 'Closed'):
            resolved = (created + timedelta(hours=random.randint(1, 72))).strftime('%Y-%m-%d %H:%M:%S')
        tickets.append((tid, cid, aid, issue_type, issue_desc, status, created.strftime('%Y-%m-%d %H:%M:%S'), resolved))

    cursor.executemany("INSERT INTO support_ticket VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", tickets)

    # ==================== FEEDBACK (200) ====================
    print("[7/8] Inserting 200 feedback entries...")
    feedbacks = []
    for i in range(200):
        fid = 6001 + i
        cid = random.choice(customer_ids)
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
        comment = random.choice(FEEDBACK_COMMENTS[rating])
        fdate = random_date(start_date, end_date)
        feedbacks.append((fid, cid, rating, comment, fdate.strftime('%Y-%m-%d %H:%M:%S')))

    cursor.executemany("INSERT INTO feedback VALUES (%s,%s,%s,%s,%s)", feedbacks)

    # ==================== CALL LOGS (250) ====================
    print("[7b] Inserting 250 call logs...")
    calls = []
    for i in range(250):
        callid = 7001 + i
        cid = random.choice(customer_ids)
        aid = random.choice(agent_ids)
        cdate = random_date(start_date, end_date)
        duration = random.randint(2, 25)
        purpose = random.choice(CALL_PURPOSES)
        calls.append((callid, cid, aid, cdate.strftime('%Y-%m-%d %H:%M:%S'), duration, purpose))

    cursor.executemany("INSERT INTO call_log VALUES (%s,%s,%s,%s,%s,%s)", calls)

    # ==================== WEB INTERACTIONS (800) ====================
    print("[8/8] Inserting 800 web interactions...")
    interactions = []
    for i in range(800):
        intid = 8001 + i
        cid = random.choice(customer_ids)
        itype = random.choice(INTERACTION_TYPES)
        page = random.choice(PAGES_VISITED)
        itime = random_date(start_date, end_date)
        ip = random_ip()
        interactions.append((intid, cid, itype, page, itime.strftime('%Y-%m-%d %H:%M:%S'), ip))

    cursor.executemany("INSERT INTO web_interaction VALUES (%s,%s,%s,%s,%s,%s)", interactions)

    conn.commit()
    conn.close()

    print("\n" + "=" * 50)
    print("  DATABASE SEEDED SUCCESSFULLY!")
    print("=" * 50)
    print(f"  Customers:        150")
    print(f"  Products:          {len(PRODUCTS)}")
    print(f"  Orders:           400")
    print(f"  Order Details:    {len(order_details_list)}")
    print(f"  Support Agents:     8")
    print(f"  Support Tickets:  120")
    print(f"  Feedback:         200")
    print(f"  Call Logs:        250")
    print(f"  Web Interactions: 800")
    print("=" * 50)


if __name__ == '__main__':
    seed()
