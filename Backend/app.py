from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_connection
import datetime
import decimal

# ============================================================
#  FLASK APP SETUP
# ============================================================

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API


# ============================================================
#  HELPER FUNCTIONS
# ============================================================

def serialize(value):
    """Convert special Python types to JSON-friendly format."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value


def rows_to_list(cursor, rows):
    """Convert database rows into a list of dictionaries."""
    columns = [desc[0] for desc in cursor.description]
    return [
        {col: serialize(val) for col, val in zip(columns, row)}
        for row in rows
    ]


def row_to_dict(cursor, row):
    """Convert a single database row into a dictionary."""
    columns = [desc[0] for desc in cursor.description]
    return {col: serialize(val) for col, val in zip(columns, row)}


# ============================================================
#  LOGIN API
# ============================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Verify username and password, return user info."""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, username, full_name, role, email, dept
        FROM users WHERE username = %s AND password = %s
    """, (username, password))

    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "success": True,
            "user": {
                "user_id": row[0],
                "username": row[1],
                "full_name": row[2],
                "role": row[3],
                "email": row[4],
                "dept": row[5]
            }
        })
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


# ============================================================
#  SEARCH API
# ============================================================

@app.route('/api/search')
def search():
    """Search across customers, orders, tickets by keyword."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_connection()
    cursor = conn.cursor()

    results = []

    # Search customers
    cursor.execute("""
        SELECT customer_id, name, email, phone_no, city
        FROM customer
        WHERE name LIKE %s OR email LIKE %s OR phone_no LIKE %s
        LIMIT 10
    """, (f'%{q}%', f'%{q}%', f'%{q}%'))
    for row in cursor.fetchall():
        results.append({
            "type": "customer", "id": row[0],
            "title": row[1], "subtitle": f"{row[2]} | {row[4]}",
            "link": f"customer360.html?id={row[0]}"
        })

    # Search orders by ID
    cursor.execute("""
        SELECT o.order_id, c.name, o.total_amount, o.order_status
        FROM orders o JOIN customer c ON o.customer_id = c.customer_id
        WHERE CAST(o.order_id AS CHAR) LIKE %s OR c.name LIKE %s
        LIMIT 10
    """, (f'%{q}%', f'%{q}%'))
    for row in cursor.fetchall():
        results.append({
            "type": "order", "id": row[0],
            "title": f"Order #{row[0]}", "subtitle": f"{row[1]} | {row[3]}",
            "link": "orders.html"
        })

    conn.close()
    return jsonify(results)


# ============================================================
#  DASHBOARD APIs
# ============================================================

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Return KPI numbers for the dashboard cards."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customer")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders")
    total_revenue = float(cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM support_ticket WHERE status = 'Open'")
    open_tickets = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "open_tickets": open_tickets
    })


@app.route('/api/dashboard/revenue-chart')
def dashboard_revenue_chart():
    """Return monthly revenue data for the line chart."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE_FORMAT(order_date, '%b') AS month,
               SUM(total_amount) AS revenue
        FROM orders
        GROUP BY MONTH(order_date), DATE_FORMAT(order_date, '%b')
        ORDER BY MONTH(order_date)
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in rows]
    data = [float(row[1]) for row in rows]

    return jsonify({"labels": labels, "data": data})


@app.route('/api/dashboard/segments')
def dashboard_segments():
    """Return customer count per segment for the doughnut chart."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cs.segment_type, COUNT(c.customer_id) AS count
        FROM customer c
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        GROUP BY cs.segment_type
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in rows]
    data = [row[1] for row in rows]

    return jsonify({"labels": labels, "data": data})


@app.route('/api/dashboard/recent-activity')
def dashboard_recent_activity():
    """Return recent activities from orders, tickets, and feedback."""
    conn = get_connection()
    cursor = conn.cursor()

    activities = []

    # Recent orders
    cursor.execute("""
        SELECT c.name, o.total_amount, o.order_date
        FROM orders o JOIN customer c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC LIMIT 3
    """)
    for row in cursor.fetchall():
        activities.append({
            "text": f"{row[0]} placed an order — ₹{float(row[1]):,.0f}",
            "time": serialize(row[2]),
            "color": "green"
        })

    # Recent tickets
    cursor.execute("""
        SELECT c.name, st.issue_type, st.created_date
        FROM support_ticket st JOIN customer c ON st.customer_id = c.customer_id
        ORDER BY st.created_date DESC LIMIT 3
    """)
    for row in cursor.fetchall():
        activities.append({
            "text": f"{row[0]} raised a ticket — {row[1]}",
            "time": serialize(row[2]),
            "color": "amber"
        })

    # Recent feedback
    cursor.execute("""
        SELECT c.name, f.rating, f.feedback_date
        FROM feedback f JOIN customer c ON f.customer_id = c.customer_id
        ORDER BY f.feedback_date DESC LIMIT 3
    """)
    for row in cursor.fetchall():
        activities.append({
            "text": f"{row[0]} left a {row[1]}-star review",
            "time": serialize(row[2]),
            "color": "purple"
        })

    # Sort all activities by time (newest first)
    activities.sort(key=lambda x: x["time"], reverse=True)

    conn.close()
    return jsonify(activities)


# ============================================================
#  CUSTOMER APIs
# ============================================================

@app.route('/api/customers')
def get_customers():
    """Return all customers with their segment name."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.customer_id, c.name, c.email, c.phone_no, c.gender,
               c.dob, c.city, c.state, c.pincode,
               cs.segment_type
        FROM customer c
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        ORDER BY c.customer_id
    """)
    customers = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(customers)


@app.route('/api/customers/stats')
def customers_stats():
    """Return KPI stats for the customers page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customer")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM customer c
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        WHERE cs.segment_type = 'Premium'
    """)
    premium = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM customer c
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        WHERE cs.segment_type = 'Regular'
    """)
    regular = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM customer c
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        WHERE cs.segment_type = 'New'
    """)
    new_count = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total": total,
        "premium": premium,
        "regular": regular,
        "new": new_count
    })


@app.route('/api/customers/<int:customer_id>')
def get_customer(customer_id):
    """Return full details of a single customer (for Customer 360)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.customer_id, c.name, c.email, c.phone_no, c.gender,
               c.dob, c.city, c.state, c.pincode,
               cs.segment_type
        FROM customer c
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        WHERE c.customer_id = %s
    """, (customer_id,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Customer not found"}), 404

    customer = row_to_dict(cursor, row)

    # Get customer's stats
    cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = %s", (customer_id,))
    customer["total_orders"] = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id = %s", (customer_id,))
    customer["lifetime_value"] = float(cursor.fetchone()[0])

    cursor.execute("SELECT COALESCE(AVG(rating), 0) FROM feedback WHERE customer_id = %s", (customer_id,))
    customer["avg_rating"] = round(float(cursor.fetchone()[0]), 1)

    cursor.execute("SELECT COUNT(*) FROM support_ticket WHERE customer_id = %s", (customer_id,))
    customer["ticket_count"] = cursor.fetchone()[0]

    conn.close()
    return jsonify(customer)


@app.route('/api/customers/<int:customer_id>/timeline')
def customer_timeline(customer_id):
    """Return all activities of a customer as a timeline."""
    conn = get_connection()
    cursor = conn.cursor()

    timeline = []

    # Orders
    cursor.execute("""
        SELECT order_id, total_amount, order_status, order_date
        FROM orders WHERE customer_id = %s
    """, (customer_id,))
    for row in cursor.fetchall():
        timeline.append({
            "type": "order",
            "icon": "🛒",
            "title": f"Order #{row[0]} — {row[2]}",
            "detail": f"₹{float(row[1]):,.0f}",
            "time": serialize(row[3])
        })

    # Tickets
    cursor.execute("""
        SELECT ticket_id, issue_type, status, created_date
        FROM support_ticket WHERE customer_id = %s
    """, (customer_id,))
    for row in cursor.fetchall():
        timeline.append({
            "type": "ticket",
            "icon": "🎫",
            "title": f"Ticket #{row[0]} — {row[1]}",
            "detail": row[2],
            "time": serialize(row[3])
        })

    # Feedback
    cursor.execute("""
        SELECT feedback_id, rating, comments, feedback_date
        FROM feedback WHERE customer_id = %s
    """, (customer_id,))
    for row in cursor.fetchall():
        timeline.append({
            "type": "feedback",
            "icon": "⭐",
            "title": f"Left {row[1]}-star review",
            "detail": row[2],
            "time": serialize(row[3])
        })

    # Calls
    cursor.execute("""
        SELECT call_id, call_purpose, call_duration, call_date
        FROM call_log WHERE customer_id = %s
    """, (customer_id,))
    for row in cursor.fetchall():
        timeline.append({
            "type": "call",
            "icon": "📞",
            "title": f"Call — {row[1]}",
            "detail": f"{row[2]} min",
            "time": serialize(row[3])
        })

    # Web interactions
    cursor.execute("""
        SELECT interaction_type, page_visited, interaction_time
        FROM web_interaction WHERE customer_id = %s
    """, (customer_id,))
    for row in cursor.fetchall():
        timeline.append({
            "type": "interaction",
            "icon": "🌐",
            "title": f"{row[0]} — {row[1]}",
            "detail": "",
            "time": serialize(row[2])
        })

    # Sort by time (newest first)
    timeline.sort(key=lambda x: x["time"], reverse=True)

    conn.close()
    return jsonify(timeline)


@app.route('/api/customers/<int:customer_id>/orders')
def customer_orders(customer_id):
    """Return all orders of a specific customer."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT order_id, order_date, total_amount, payment_method, order_status
        FROM orders WHERE customer_id = %s
        ORDER BY order_date DESC
    """, (customer_id,))
    orders = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(orders)


@app.route('/api/customers', methods=['POST'])
def add_customer():
    """Add a new customer to the database."""
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    # Auto-generate next customer_id
    cursor.execute("SELECT COALESCE(MAX(customer_id), 1000) + 1 FROM customer")
    new_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO customer (customer_id, name, email, phone_no, gender, dob,
                              city, state, pincode, segment_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        new_id, data['name'], data['email'], data['phone_no'],
        data['gender'], data.get('dob', '2000-01-01'), data['city'], data['state'],
        data['pincode'], data['segment_id']
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Customer added successfully", "customer_id": new_id}), 201


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update an existing customer."""
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customer
        SET name=%s, email=%s, phone_no=%s, gender=%s, dob=%s,
            city=%s, state=%s, pincode=%s, segment_id=%s
        WHERE customer_id=%s
    """, (
        data['name'], data['email'], data['phone_no'], data['gender'],
        data['dob'], data['city'], data['state'], data['pincode'],
        data['segment_id'], customer_id
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Customer updated successfully"})


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Customer deleted successfully"})


# ============================================================
#  ORDER APIs
# ============================================================

@app.route('/api/orders')
def get_orders():
    """Return all orders with customer names."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.order_id, c.name AS customer_name, o.order_date,
               o.total_amount, o.payment_method, o.order_status
        FROM orders o
        JOIN customer c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
    """)
    orders = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(orders)


@app.route('/api/orders/stats')
def orders_stats():
    """Return KPI stats for the orders page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders")
    revenue = float(cursor.fetchone()[0])

    cursor.execute("SELECT COALESCE(AVG(total_amount), 0) FROM orders")
    avg_value = round(float(cursor.fetchone()[0]), 0)

    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Processing'")
    pending = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total": total,
        "revenue": revenue,
        "avg_value": avg_value,
        "pending": pending
    })


# ============================================================
#  SUPPORT TICKET APIs
# ============================================================

@app.route('/api/tickets')
def get_tickets():
    """Return all tickets with customer and agent names."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT st.ticket_id, c.name AS customer_name,
               sa.agent_name, st.issue_type, st.issue_desc,
               st.status, st.created_date, st.resolved_date
        FROM support_ticket st
        JOIN customer c ON st.customer_id = c.customer_id
        JOIN support_agent sa ON st.agent_id = sa.agent_id
        ORDER BY st.created_date DESC
    """)
    tickets = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(tickets)


@app.route('/api/tickets/stats')
def tickets_stats():
    """Return KPI stats for the tickets page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM support_ticket WHERE status = 'Open'")
    open_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM support_ticket WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM support_ticket WHERE status = 'Closed'")
    closed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(AVG(TIMESTAMPDIFF(HOUR, created_date, resolved_date)), 0)
        FROM support_ticket
        WHERE resolved_date IS NOT NULL
    """)
    avg_resolution = round(float(cursor.fetchone()[0]), 1)

    total = open_count + resolved + closed

    conn.close()

    return jsonify({
        "total": total,
        "open": open_count,
        "resolved": resolved,
        "closed": closed,
        "avg_resolution_hours": avg_resolution
    })


# ============================================================
#  FEEDBACK APIs
# ============================================================

@app.route('/api/feedback')
def get_feedback():
    """Return all feedback with customer names."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.feedback_id, c.name AS customer_name,
               cs.segment_type, f.rating, f.comments, f.feedback_date
        FROM feedback f
        JOIN customer c ON f.customer_id = c.customer_id
        JOIN customer_segment cs ON c.segment_id = cs.segment_id
        ORDER BY f.feedback_date DESC
    """)
    feedback = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(feedback)


@app.route('/api/feedback/stats')
def feedback_stats():
    """Return KPI stats for the feedback page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(AVG(rating), 0) FROM feedback")
    avg_rating = round(float(cursor.fetchone()[0]), 1)

    cursor.execute("SELECT COUNT(*) FROM feedback")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating >= 4")
    positive = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating <= 2")
    negative = cursor.fetchone()[0]

    positive_pct = round((positive / total * 100), 0) if total > 0 else 0
    negative_pct = round((negative / total * 100), 0) if total > 0 else 0

    conn.close()

    return jsonify({
        "avg_rating": avg_rating,
        "total": total,
        "positive_pct": positive_pct,
        "negative_pct": negative_pct
    })


# ============================================================
#  CALL LOG APIs
# ============================================================

@app.route('/api/calls')
def get_calls():
    """Return all call logs with customer and agent names."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cl.call_id, c.name AS customer_name,
               sa.agent_name, cl.call_date, cl.call_duration,
               cl.call_purpose
        FROM call_log cl
        JOIN customer c ON cl.customer_id = c.customer_id
        JOIN support_agent sa ON cl.agent_id = sa.agent_id
        ORDER BY cl.call_date DESC
    """)
    calls = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(calls)


@app.route('/api/calls/stats')
def calls_stats():
    """Return KPI stats for the call logs page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM call_log")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(AVG(call_duration), 0) FROM call_log")
    avg_duration = round(float(cursor.fetchone()[0]), 1)

    conn.close()

    return jsonify({
        "total": total,
        "avg_duration_min": avg_duration
    })


# ============================================================
#  WEB INTERACTION APIs
# ============================================================

@app.route('/api/interactions')
def get_interactions():
    """Return all web interactions with customer names."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wi.interaction_id, c.name AS customer_name,
               wi.interaction_type, wi.page_visited,
               wi.interaction_time, wi.ip_address
        FROM web_interaction wi
        JOIN customer c ON wi.customer_id = c.customer_id
        ORDER BY wi.interaction_time DESC
    """)
    interactions = rows_to_list(cursor, cursor.fetchall())
    conn.close()

    return jsonify(interactions)


@app.route('/api/interactions/stats')
def interactions_stats():
    """Return KPI stats for the web interactions page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM web_interaction")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM web_interaction")
    unique_visitors = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM web_interaction
        WHERE interaction_type = 'Page View'
    """)
    page_views = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM web_interaction
        WHERE interaction_type = 'Click'
    """)
    clicks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM web_interaction
        WHERE interaction_type = 'Form Submit'
    """)
    form_submits = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total": total,
        "unique_visitors": unique_visitors,
        "page_views": page_views,
        "clicks": clicks,
        "form_submits": form_submits
    })


# ============================================================
#  RUN THE SERVER
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("  CRM 360 Backend Server")
    print("  Running on http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
