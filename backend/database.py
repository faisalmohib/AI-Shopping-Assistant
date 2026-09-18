import sqlite3

DB_PATH = "products.db"


def query_products(sql: str):

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute(sql)

    rows = cur.fetchall()

    conn.close()

    return rows


def create_order(
    user_id,
    product_id,
    product_name,
    customer_name,
    phone,
    address,
    quantity
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders (
            user_id,
            product_id,
            product_name,
            customer_name,
            phone,
            address,
            quantity
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        product_id,
        product_name,
        customer_name,
        phone,
        address,
        quantity
    ))

    conn.commit()
    conn.close()

def get_user_orders(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            total_amount,
            created_at
        FROM order_groups
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows

def get_order_items(order_group_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            product_name,
            quantity,
            price
        FROM order_items
        WHERE order_group_id = ?
    """, (order_group_id,))

    rows = cur.fetchall()

    conn.close()

    return rows

def add_to_cart(
    user_id,
    product_id,
    size,
    quantity=1
):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT quantity
        FROM cart
        WHERE user_id = ?
        AND product_id = ?
        AND size = ?
    """, (
        user_id,
        product_id,
        size
    ))

    existing = cur.fetchone()

    if existing:

        cur.execute("""
            UPDATE cart
            SET quantity = quantity + ?
            WHERE user_id = ?
            AND product_id = ?
            AND size = ?
        """, (
            quantity,
            user_id,
            product_id,
            size
        ))

    else:

        cur.execute("""
            INSERT INTO cart(
                user_id,
                product_id,
                quantity,
                size
            )
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            product_id,
            quantity,
            size
        ))

    conn.commit()
    conn.close()

def get_cart_items(user_id):

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.id,
            p.id,
            p.name,
            p.price,
            p.image,
            p.color,
            p.brand,
            c.quantity,
            c.size
        FROM cart c
        JOIN products p
            ON c.product_id = p.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows


def remove_from_cart(cart_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM cart
        WHERE id = ?
    """, (cart_id,))

    conn.commit()
    conn.close()

def clear_cart(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM cart
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def create_cart_order(
    user_id,
    customer_name,
    phone,
    address
):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.name,
            p.price,
            c.quantity
        FROM cart c
        JOIN products p
            ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))

    cart_items = cur.fetchall()

    if not cart_items:
        conn.close()
        return False

    total_amount = sum(
        price * quantity
        for _, _, price, quantity in cart_items
    )

    cur.execute("""
        INSERT INTO order_groups (
            user_id,
            customer_name,
            phone,
            address,
            total_amount
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        customer_name,
        phone,
        address,
        total_amount
    ))

    order_group_id = cur.lastrowid

    for product_id, product_name, price, quantity in cart_items:

        cur.execute("""
            INSERT INTO order_items (
                order_group_id,
                product_id,
                product_name,
                quantity,
                price
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            order_group_id,
            product_id,
            product_name,
            quantity,
            price
        ))

    cur.execute("""
        DELETE FROM cart
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return order_group_id


def get_cart_total(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            SUM(p.price * c.quantity)
        FROM cart c
        JOIN products p
            ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))

    total = cur.fetchone()[0]

    conn.close()

    return total or 0



def create_direct_order(
    user_id,
    product_id,
    customer_name,
    phone,
    address,
    quantity
):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get product information
    cur.execute("""
        SELECT name, price
        FROM products
        WHERE id = ?
    """, (product_id,))

    product = cur.fetchone()

    if not product:
        conn.close()
        return None

    product_name = product[0]
    price = product[1]

    total = price * quantity

    # Create order group
    cur.execute("""
        INSERT INTO order_groups (
            user_id,
            total_amount,
            created_at
        )
        VALUES (?, ?, datetime('now'))
    """, (
        user_id,
        total
    ))

    order_id = cur.lastrowid

    # Create order item
    cur.execute("""
        INSERT INTO order_items (
            order_id,
            product_id,
            product_name,
            price,
            quantity
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        order_id,
        product_id,
        product_name,
        price,
        quantity
    ))

    conn.commit()
    conn.close()

    return order_id

def add_to_wishlist(user_id, product_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM wishlist
        WHERE user_id=?
        AND product_id=?
    """, (user_id, product_id))

    if cur.fetchone():

        conn.close()

        return False

    cur.execute("""
        INSERT INTO wishlist(
            user_id,
            product_id
        )
        VALUES (?,?)
    """, (
        user_id,
        product_id
    ))

    conn.commit()
    conn.close()

    return True

def get_wishlist(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            w.id,
            p.id,
            p.name,
            p.price,
            p.color,
            p.brand,
            p.image,
            p.url
        FROM wishlist w
        JOIN products p
        ON w.product_id = p.id
        WHERE w.user_id = ?
        ORDER BY w.created_at DESC
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows

def remove_from_wishlist(wishlist_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM wishlist
        WHERE id = ?
    """, (wishlist_id,))

    conn.commit()
    conn.close()

def clear_wishlist(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM wishlist
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()



# =========================
# SAVE SEARCH QUERY
# =========================
def save_search_query(user_id, query):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO search_history (user_id, query)
        VALUES (?, ?)
    """, (user_id, query))

    conn.commit()
    conn.close()


# =========================
# GET SEARCH HISTORY
# =========================
def get_search_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT query, created_at
        FROM search_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return rows


def add_recently_viewed(user_id, product_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # remove duplicates first
    cur.execute("""
        DELETE FROM recently_viewed
        WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id))

    cur.execute("""
        INSERT INTO recently_viewed (user_id, product_id)
        VALUES (?, ?)
    """, (user_id, product_id))

    conn.commit()
    conn.close()

def get_recently_viewed(user_id, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT p.*
        FROM recently_viewed r
        JOIN products p ON p.id = r.product_id
        WHERE r.user_id = ?
        ORDER BY r.viewed_at DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cur.fetchall()
    conn.close()

    return rows


def get_recent_searches(
    user_id,
    limit=5
):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT query
        FROM search_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]


def get_recently_viewed_ids(
    user_id,
    limit=5
):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT product_id
        FROM recently_viewed
        WHERE user_id = ?
        ORDER BY viewed_at DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]


def get_wishlist_ids(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT product_id
        FROM wishlist
        WHERE user_id = ?
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]


def get_cart_product_ids(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT product_id
        FROM cart
        WHERE user_id = ?
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]







# djfkkkkkkkkkkkkkjfssssssssssssssssssssssssssss

def get_product_by_id(product_id):

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM PRODUCTS
        WHERE id = ?
    """, (product_id,))

    product = cur.fetchone()

    conn.close()

    return product


def get_product_sizes(shopify_product_id):

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""
        SELECT size, available
        FROM PRODUCT_VARIANTS
        WHERE product_id = ?
    """, (shopify_product_id,))

    sizes = cur.fetchall()

    conn.close()

    return sizes


def get_product(product_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,))

    row = cur.fetchone()

    conn.close()

    return row


def create_payment_profiles_table():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone TEXT,
            address TEXT,
            card_number TEXT,
            expiry TEXT,
            cvv TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_payment_profile(user_id, phone, address, card_number, expiry, cvv):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM payment_profiles
        WHERE user_id = ?
    """, (user_id,))

    existing = cur.fetchone()

    if existing:

        cur.execute("""
            UPDATE payment_profiles
            SET phone = ?,
                address = ?,
                card_number = ?,
                expiry = ?,
                cvv = ?
            WHERE user_id = ?
        """, (
            phone,
            address,
            card_number,
            expiry,
            cvv,
            user_id
        ))

    else:

        cur.execute("""
            INSERT INTO payment_profiles (
                user_id,
                phone,
                address,
                card_number,
                expiry,
                cvv
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            phone,
            address,
            card_number,
            expiry,
            cvv
        ))

    conn.commit()
    conn.close()

def get_payment_profile(user_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT phone, address, card_number, expiry, cvv
        FROM payment_profiles
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "phone": row[0],
        "address": row[1],
        "card_number": row[2],
        "expiry": row[3],
        "cvv": row[4]
    }

def create_direct_order(
    user_id,
    product_id,
    product_name,
    price,
    customer_name,
    phone,
    address,
    quantity
):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Create order group
    cur.execute("""
        INSERT INTO order_groups (
            user_id,
            total_amount,
            created_at
        )
        VALUES (?, ?, datetime('now'))
    """, (
        user_id,
        price * quantity
    ))

    order_group_id = cur.lastrowid

    # 2. Create order item
    cur.execute("""
        INSERT INTO order_items (
            order_group_id,
            product_id,
            product_name,
            price,
            quantity
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        order_group_id,
        product_id,
        product_name,
        price,
        quantity
    ))

    conn.commit()
    conn.close()

    return order_group_id

