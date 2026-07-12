import mysql.connector

def get_connection():
    print("Connecting to:", "canteen-kiosk-db.cv6mcw60oobd.ap-south-1.rds.amazonaws.com")
    return mysql.connector.connect(
        host="canteen-kiosk-db.cv6mcw60oobd.ap-south-1.rds.amazonaws.com",
        user="admin",
        password="keersiri123",
        database="canteen_kiosk"
    )