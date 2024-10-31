import sqlite3
from sqlite3 import Error
from faker import Faker
import random
from datetime import datetime, timedelta

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(connection):
    cursor = connection.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        password TEXT NOT NULL,
        phone_number TEXT,
        is_admin NUMERIC NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Addresses (
        address_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_code INTEGER,
        street TEXT,
        num INTEGER,
        city TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    );

    CREATE TABLE IF NOT EXISTS Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Brands (
        brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Discounts (
        discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
        percent REAL,
        end_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        valid_amount INTEGER DEFAULT 0,
        category_id INTEGER,
        brand_id INTEGER,
        discount_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES Categories(category_id),
        FOREIGN KEY (brand_id) REFERENCES Brands(brand_id),
        FOREIGN KEY (discount_id) REFERENCES Discounts(discount_id)
    );

    CREATE TABLE IF NOT EXISTS Reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        user_email TEXT,
        text TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES Products(product_id),
        FOREIGN KEY (user_email) REFERENCES Users(email)
    );

    CREATE TABLE IF NOT EXISTS Cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        total_cost REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES Users(email)
    );

    CREATE TABLE IF NOT EXISTS Selected_item (
        Selected_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER,
        product_id INTEGER,
        number INTEGER NOT NULL,
        FOREIGN KEY (cart_id) REFERENCES Cart(cart_id),
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    );

    CREATE TABLE IF NOT EXISTS Purchase (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cart_id) REFERENCES Cart(cart_id)
    );

    CREATE TABLE IF NOT EXISTS transport_status (
        transport_id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER,
        driver TEXT,
        transport_vehicle TEXT,
        send_date TIMESTAMP,
        rec_date TIMESTAMP,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (payment_id) REFERENCES Purchase(payment_id),
        CHECK (rec_date > send_date)
    );
    """)

    connection.commit()

    
category_names = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Sports & Outdoors",
                "Health & Beauty", "Toys & Games", "Automotive", "Garden & Outdoors", "Pet Supplies",
                "Office Supplies", "Music Instruments", "Baby Products", "Tools & Hardware", "Art & Craft"]


product_names = ["Smartphone", "Running Shoes", "Cooking Pan", "Yoga Mat", "Water Bottle",
                    "Laptop", "Novel", "Coffee Maker", "Bicycle", "Backpack",
                    "Headphones", "T-shirt", "Blender", "Tent", "Electric Toothbrush",
                    "Action Camera", "Desk Lamp", "Board Game", "Drill", "Acoustic Guitar",
                    "Baby Stroller", "Paint Set", "Gaming Console", "Dog Leash", "Office Chair"]

def insert_fake_data(connection):
    fake = Faker()
    cursor = connection.cursor()

    # Insert fake data into Users
    users = []
    for _ in range(10):
        email = fake.email()
        full_name = fake.name()
        password = fake.password()
        phone_number = fake.phone_number()
        is_admin = random.choice([0, 1])
        users.append((email, full_name, password, phone_number, is_admin))
    cursor.executemany("INSERT INTO Users (email, full_name, password, phone_number, is_admin) VALUES (?, ?, ?, ?, ?)", users)

    cursor.execute("SELECT user_id FROM Users")
    user_ids = cursor.fetchall()

    #insert fake address 
    addresses = []
    for user_id in user_ids:
        post_code = fake.zipcode()
        street = fake.street_name()
        num = fake.building_number()
        city = fake.city()
        addresses.append((user_id[0], post_code, street, num, city))
    cursor.executemany("INSERT INTO Addresses (user_id, post_code, street, num, city) VALUES (?, ?, ?, ?, ?)", addresses)






    # Insert fake data into Categories
    selected_Cat = random.sample(category_names,5)
    categories = []
    for cat in selected_Cat:
        categories.append((cat,))
    cursor.executemany("INSERT INTO Categories (name) VALUES (?)", categories)

    # Insert fake data into Brands
    brands = []
    for _ in range(5):
        brands.append((fake.company(),))
    cursor.executemany("INSERT INTO Brands (name) VALUES (?)", brands)

    # Insert fake data into Discounts
    discounts = []
    for _ in range(5):
        percent = random.uniform(5.0, 25.0)
        end_date = fake.date_time_between(start_date='now', end_date='+1y').strftime("%Y-%m-%d %H:%M:%S")
        discounts.append((percent, end_date))
    cursor.executemany("INSERT INTO Discounts (percent, end_date) VALUES (?, ?)", discounts)

    # Insert fake data into Products
    products = []
    for _ in range(10):
        name = random.choice(product_names)
        price = random.uniform(10.0, 500.0)
        valid_amount = random.randint(0, 200)
        category_id = random.randint(1, 5)
        brand_id = random.randint(1, 5)
        discount_id = random.choice([None, random.randint(1, 5)])
        products.append((name, price, valid_amount, category_id, brand_id, discount_id))
    cursor.executemany("INSERT INTO Products (name, price, valid_amount, category_id, brand_id, discount_id) VALUES (?, ?, ?, ?, ?, ?)", products)

    # Insert fake data into Reviews
    reviews = []
    for _ in range(10):
        product_id = random.randint(1, 10)
        user_email = random.choice(users)[0]
        reviews.append((product_id, user_email, fake.sentence()))
    cursor.executemany("INSERT INTO Reviews (product_id, user_email, text) VALUES (?, ?, ?)", reviews)

    # Insert fake data into Cart
    carts = []
    random_users = random.choices(users, k=5)
    for user in random_users:
        user_email = user[0]
        carts.append((user_email, 0))
    cursor.executemany("INSERT INTO Cart (user_email, total_cost) VALUES (?, ?)", carts)

    # Insert fake data into Selected_item
    selected_items = []
    for cart_id in range(1, 6):
        for _ in range(random.randint(0, 5)):
            product_id = random.randint(1, 10)
            number = random.randint(1, 5)
            selected_items.append((cart_id, product_id, number))
    cursor.executemany("INSERT INTO Selected_item (cart_id, product_id, number) VALUES (?, ?, ?)", selected_items)

    # Insert fake data into Purchase
    purchases = []
    for cart_id in range(1, 5):
        purchases.append((cart_id,))
    cursor.executemany("INSERT INTO Purchase (cart_id) VALUES (?)", purchases)

    # Insert fake data into transport_status
    transport_statuses = []
    for payment_id in range(len(purchases)+1):
        if payment_id==0:continue
        driver = fake.name()
        transport_vehicle = fake.license_plate()  # Using license plate as a substitute for vehicle
        send_date = fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S")
        rec_date = (datetime.strptime(send_date, "%Y-%m-%d %H:%M:%S") + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d %H:%M:%S")
        transport_statuses.append((payment_id, driver, transport_vehicle, send_date, rec_date))
    cursor.executemany("INSERT INTO transport_status (payment_id, driver, transport_vehicle, send_date, rec_date) VALUES (?, ?, ?, ?, ?)", transport_statuses)


    sql = """
    UPDATE Cart
    SET total_cost = (
        SELECT SUM(
            CASE
                WHEN p.discount_id IS NOT NULL AND d.end_date >= CURRENT_TIMESTAMP THEN
                    p.price * (1 - d.percent / 100.0) * si.number
                ELSE
                    p.price * si.number
            END
        )
        FROM Selected_item si
        JOIN Products p ON si.product_id = p.product_id
        LEFT JOIN Discounts d ON p.discount_id = d.discount_id
        WHERE si.cart_id = Cart.cart_id
        GROUP BY si.cart_id
    )
    WHERE cart_id = ?
    """
    for cart_id in range(len(carts)+1):
        try:
            cursor.execute(sql, (cart_id,))
            print("Cart total cost updated successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    connection.commit()


    
def main():
    database = "test.db"

    # Create a database connection
    conn = create_connection(database)

    # Create tables
    if conn is not None:
        create_tables(conn)

        # Insert fake data into tables
        insert_fake_data(conn)

        print("Fake data inserted successfully")

    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
