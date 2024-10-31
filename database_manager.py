import sqlite3
from sqlite3 import Error

def connect_to_database(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def close_connection(connection):
    if connection:
        connection.close()
        print("Connection closed")

def add_data(connection, table_name, data):
    cursor = connection.cursor()
    placeholders = ", ".join(["?"] * len(data))
    columns = ", ".join(data.keys())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    try:
        cursor.execute(sql, list(data.values()))
        connection.commit()
        print("Data added successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


# def delete_data(connection, table_name, condition):
#     cursor = connection.cursor()
#     sql = f"DELETE FROM {table_name} WHERE {condition}"
#     try:
#         cursor.execute(sql)
#         connection.commit()
#         print("Data deleted successfully")
#     except Error as e:
#         print(f"The error '{e}' occurred")



def delete_data(connection, table_name, condition, user_email):
    cursor = connection.cursor()
    
    # Check if the user is an admin
    try:
        cursor.execute("SELECT is_admin FROM Users WHERE email = ?", (user_email,))
        result = cursor.fetchone()
        if result is None:
            print("User does not exist")
            return
        is_admin = result[0]
    except Error as e:
        print(f"The error '{e}' occurred while checking admin status")
        return
    
    # Proceed with deletion if the user is an admin
    if is_admin:
        sql = f"DELETE FROM {table_name} WHERE {condition}"
        try:
            cursor.execute(sql)
            connection.commit()
            print("Data deleted successfully")
        except Error as e:
            print(f"The error '{e}' occurred while deleting data")
    else:
        print("Permission denied: User is not an admin")



def update_user_info(connection, email, new_data):
    cursor = connection.cursor()
    set_clause = ", ".join([f"{key} = ?" for key in new_data.keys()])
    sql = f"UPDATE Users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE email = ?"
    try:
        cursor.execute(sql, list(new_data.values()) + [email])
        connection.commit()
        print("User information updated successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def track_order_status(connection, order_id):
    cursor = connection.cursor()
    sql = """
    SELECT p.payment_id, p.date, ts.driver, ts.transport_vehicle, ts.send_date, ts.rec_date
    FROM Purchase p
    JOIN transport_status ts ON p.payment_id = ts.payment_id
    WHERE p.payment_id = ?
    """
    try:
        cursor.execute(sql, (order_id,))
        status = cursor.fetchall()
        if status:
            for record in status:
                print(f"Payment ID: {record[0]}, Order Date: {record[1]}, Driver: {record[2]}, Vehicle: {record[3]}, Send Date: {record[4]}, Receive Date: {record[5]}")
        else:
            print("Order not found")
    except Error as e:
        print(f"The error '{e}' occurred")



def view_cart_details(connection, order_id):
    cursor = connection.cursor()
    sql = """
    SELECT si.cart_id, si.product_id, p.name, si.number, p.price, 
           CASE
               WHEN p.discount_id IS NOT NULL AND d.end_date >= CURRENT_TIMESTAMP THEN
                   p.price * (1 - d.percent / 100.0)
               ELSE
                   p.price
           END AS discounted_price
    FROM Selected_item si
    JOIN Products p ON si.product_id = p.product_id
    LEFT JOIN Discounts d ON p.discount_id = d.discount_id
    WHERE si.cart_id = ?
    """
    try:
        cursor.execute(sql, (order_id,))
        details = cursor.fetchall()
        if details:
            print(f"Cart ID: {order_id}")
            for record in details:
                print(f"Product ID: {record[1]}, Product Name: {record[2]}, Quantity: {record[3]}, Price per Unit: {record[4]}, after discount: {record[5]}")
        else:
            print("Order not found")
    except Error as e:
        print(f"The error '{e}' occurred")



def calculate_cart_total(connection, cart_id):
    cursor = connection.cursor()
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
    try:
        cursor.execute(sql, (cart_id,))
        connection.commit()
        print("Cart total cost updated successfully")
    except Error as e:
        print(f"The error '{e}' occurred")



def get_purchase_history(connection, user_email):
    cursor = connection.cursor()
    sql = """
    SELECT p.payment_id, p.date, c.total_cost
    FROM Purchase p
    JOIN Cart c ON p.cart_id = c.cart_id
    WHERE c.user_email = ?
    ORDER BY p.date DESC
    """
    try:
        cursor.execute(sql, (user_email,))
        history = cursor.fetchall()
        if history:
            print(f"user:{user_email}")
            for record in history:
                print(f"Payment ID: {record[0]}, Date: {record[1]}, Total Cost: {record[2]}")
        else:
            print("No purchase history found for this user")
    except Error as e:
        print(f"The error '{e}' occurred")



def view_reviews(connection, product_id):
    cursor = connection.cursor()
    sql = """
    SELECT r.review_id, r.user_email, u.full_name, r.text, r.date
    FROM Reviews r
    JOIN Users u ON r.user_email = u.email
    WHERE r.product_id = ?
    ORDER BY r.date DESC
    """
    try:
        cursor.execute(sql, (product_id,))
        reviews = cursor.fetchall()
        if reviews:
            print(f"rewiews for product by id :{product_id}")
            for record in reviews:
                print(f"Review ID: {record[0]}, User Email: {record[1]}, User Name: {record[2]}, Review Text: {record[3]}, Date: {record[4]}")
        else:
            print("No reviews found for this product")
    except Error as e:
        print(f"The error '{e}' occurred")



def track_transport_status(connection, order_id):
    cursor = connection.cursor()
    sql = """
    SELECT ts.transport_id, ts.payment_id, ts.driver, ts.transport_vehicle, ts.send_date, ts.rec_date
    FROM transport_status ts
    WHERE ts.payment_id = ?
    """
    try:
        cursor.execute(sql, (order_id,))
        status = cursor.fetchall()
        if status:
            print(f"transport info for payment id:{order_id}")
            for record in status:
                print(f"Transport ID: {record[0]}, Payment ID: {record[1]}, Driver: {record[2]}, Vehicle: {record[3]}, Send Date: {record[4]}, Receive Date: {record[5]}")
        else:
            print("Shipping status not found")
    except Error as e:
        print(f"The error '{e}' occurred")


def drop_all_tables(connection):
    cursor = connection.cursor()
    
    # Get the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Drop each table
    for table_name in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name[0]};")
            print(f"Table {table_name[0]} dropped successfully")
        except Error as e:
            print(f"The error '{e}' occurred")


if __name__ == "__main__":
    connection = connect_to_database("test.db")

    drop_all_tables(connection)

    # Add new user example
    # new_user = {
    #     "email": "test@example.com",
    #     "full_name": "test",
    #     "password": "password",
    #     "phone_number": "1234567890",
    #     "is_admin": 0,
    #     "address": "User Address"
    # }
    # add_data(connection, "Users", new_user)

    # # Update user information example
    # updated_info = {
    #     "full_name": "Updated Full Name",
    #     "phone_number": "0987654321",
    #     "address": "Updated Address"
    # }
    # update_user_info(connection, "user4@example.com", updated_info)

    # # Add new product example
    # new_product = {
    #     "name": "New Product",
    #     "price": 99.99,
    #     "valid_amount": 10,
    #     "category_id": 1,
    #     "brand_id": 1,
    #     "discount_id": 1
    # }
    # add_data(connection, "Products", new_product)

    # # Delete old product example
    #delete_data(connection, "Reviews", "review_id = 1","rachelclark@example.org")

    close_connection(connection)                
