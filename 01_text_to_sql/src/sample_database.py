"""Sample SQLite database initialization with rich, accurate e-commerce data."""
import os
import sqlite3

def get_db_path(data_dir: str = None) -> str:
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "sample_ecommerce.db")

def initialize_database(db_path: str = None) -> str:
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        country TEXT NOT NULL,
        created_at DATE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM customers;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executescript("""
        INSERT INTO customers (name, email, country, created_at) VALUES
        ('Alice Smith', 'alice.smith@example.com', 'USA', '2023-01-15'),
        ('Bob Jones', 'bob.jones@example.com', 'Canada', '2023-02-20'),
        ('Charlie Brown', 'charlie.brown@example.com', 'UK', '2023-03-10'),
        ('Diana Prince', 'diana.prince@example.com', 'USA', '2023-04-05'),
        ('Evan Wright', 'evan.wright@example.com', 'Germany', '2023-05-12'),
        ('Fiona Gallagher', 'fiona.g@example.com', 'USA', '2023-06-18'),
        ('George Clark', 'george.c@example.com', 'Australia', '2023-07-22'),
        ('Hannah Abbott', 'hannah.a@example.com', 'UK', '2023-08-30'),
        ('Ian Malcolm', 'ian.m@example.com', 'USA', '2023-09-14'),
        ('Julia Roberts', 'julia.r@example.com', 'France', '2023-10-01'),
        ('Kevin Bacon', 'kevin.b@example.com', 'Canada', '2023-11-11'),
        ('Laura Croft', 'laura.c@example.com', 'UK', '2023-12-05');

        INSERT INTO products (product_name, category, price, stock_quantity) VALUES
        ('Laptop Pro 15', 'Electronics', 1299.99, 45),
        ('Wireless Mouse', 'Electronics', 29.99, 150),
        ('Noise-Canceling Headphones', 'Electronics', 199.99, 80),
        ('Ergonomic Office Chair', 'Furniture', 249.99, 25),
        ('Standing Desk', 'Furniture', 499.99, 15),
        ('Coffee Maker', 'Appliances', 89.99, 60),
        ('UltraWide 34 Monitor', 'Electronics', 599.99, 30),
        ('Mechanical Keyboard', 'Electronics', 119.99, 100),
        ('Smart LED Desk Lamp', 'Furniture', 49.99, 75),
        ('Electric Kettle', 'Appliances', 39.99, 90),
        ('Portable Power Bank', 'Electronics', 49.99, 200),
        ('Blender 1000W', 'Appliances', 79.99, 40);

        INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
        (1, '2023-06-01', 1329.98, 'Completed'),
        (2, '2023-06-03', 249.99, 'Completed'),
        (1, '2023-06-15', 199.99, 'Completed'),
        (3, '2023-06-20', 89.99, 'Shipped'),
        (4, '2023-06-22', 529.98, 'Processing'),
        (5, '2023-06-25', 1299.99, 'Completed'),
        (6, '2023-07-02', 719.98, 'Completed'),
        (7, '2023-07-10', 499.99, 'Shipped'),
        (8, '2023-07-18', 159.98, 'Completed'),
        (9, '2023-08-01', 1299.99, 'Completed'),
        (10, '2023-08-05', 89.99, 'Cancelled'),
        (11, '2023-08-12', 649.98, 'Completed'),
        (12, '2023-08-20', 249.99, 'Completed');

        INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
        (1, 1, 1, 1299.99),
        (1, 2, 1, 29.99),
        (2, 4, 1, 249.99),
        (3, 3, 1, 199.99),
        (4, 6, 1, 89.99),
        (5, 2, 1, 29.99),
        (5, 5, 1, 499.99),
        (6, 1, 1, 1299.99),
        (7, 7, 1, 599.99),
        (7, 8, 1, 119.99),
        (8, 5, 1, 499.99),
        (9, 8, 1, 119.99),
        (9, 10, 1, 39.99),
        (10, 1, 1, 1299.99),
        (11, 6, 1, 89.99),
        (12, 7, 1, 599.99),
        (12, 11, 1, 49.99),
        (13, 4, 1, 249.99);
        """)

    conn.commit()
    conn.close()
    return db_path

if __name__ == "__main__":
    path = initialize_database()
    print(f"Sample database initialized at: {path}")
