import pyodbc
import mysql.connector
import json

import os
from dotenv import load_dotenv

load_dotenv()

def conectaFox(foxDB): #foxDB
    try:
        #cadena_conexion = 'DRIVER={Devart ODBC Driver for xBase};Database='+foxDB+';DBFFormat=VisualFoxPro;IgnoreMetadataErrors=True;UseFileCodepage=False;ConnectMode=Shared;CHARSET=UTF8;ConnectMode=Unsafe;RegionalNumberSettings=True;RegionalDateTimeSettings=True;'
        cadena_conexion = 'DRIVER={Devart ODBC Driver for xBase};Database='+foxDB+';DBFFormat=VisualFoxPro;IgnoreMetadataErrors=True;UseFileCodepage=False;ConnectMode=Shared;CHARSET=UTF8;ConnectMode=Unsafe;RegionalNumberSettings=True;RegionalDateTimeSettings=True;' 

        # Establecer la conexión con la base de datos.
        #conexion = pyodbc.connect(cadena_conexion)
        #cursor = conexion.cursor()
        return cadena_conexion

    except pyodbc.Error as e:
        # En caso de error, imprimir el error y devolver None o una cadena JSON de error.
        print("Error conectarse a la base de datos:", e)
        return json.dumps({'error': (e)})

def conectaMaria(database): #mariaDB
    if not database:
            database = os.getenv("DB_DATABASE", "kaisen")
    cadena_conexion = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "database": database,
        "port": int(os.getenv("DB_PORT", 3307)),
    }
    return  cadena_conexion 
    

def conectaFoxe(foxDB): #foxDB
    try:
        #cadena_conexion = 'DRIVER={Devart ODBC Driver for xBase};Database='+foxDB+';DBFFormat=VisualFoxPro;IgnoreMetadataErrors=True;UseFileCodepage=False;ConnectMode=Shared;CHARSET=UTF8;ConnectMode=Unsafe;RegionalNumberSettings=True;RegionalDateTimeSettings=True;'
        cadena_conexion = 'DRIVER={Devart ODBC Driver for xBase};Database='+foxDB+';DBFFormat=VisualFoxPro;IgnoreMetadataErrors=True;UseFileCodepage=False;ConnectMode=Exclusive;CHARSET=UTF8;ConnectMode=Unsafe;RegionalNumberSettings=True;RegionalDateTimeSettings=True;' 

        # Establecer la conexión con la base de datos.
        #conexion = pyodbc.connect(cadena_conexion)
        #cursor = conexion.cursor()
        return cadena_conexion

    except pyodbc.Error as e:
        # En caso de error, imprimir el error y devolver None o una cadena JSON de error.
        print("Error conectarse a la base de datos:", e)
        return json.dumps({'error': (e)})