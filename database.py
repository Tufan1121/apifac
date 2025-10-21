import pyodbc
import mysql.connector

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
            database="kaisen"
    cadena_conexion = {
        "user": "root",
        "password": "Nq37.321.1",
        "host": "127.0.0.1",
        "database": database,
        "port": 3307,
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