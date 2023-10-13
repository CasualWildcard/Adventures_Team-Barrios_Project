import mysql.connector
from mysql.connector import connect, Error
import pandas as pd
from getpass import getpass

def dbconnect():
    try:
        with connect(
            host="localhost",
            user=input("Enter username: "),
         password=getpass("Enter password: "),
        ) as connection:
           print(connection)
    except Error as e:
        print(e)
