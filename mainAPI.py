from fastapi import FastAPI, Query, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt
from database import conectaFox  # Importa la función de tu otro script
from database import conectaMaria  # Importa la función de tu otro script
from correo import enviarEmail
from correocotiza import enviarEmailCot, enviarEmailSimple
from enum import Enum
from typing import Union, Optional
from pydantic import BaseModel, condecimal, field_validator
from typing import Annotated
import pyodbc
import mysql.connector
import json
from dotenv import load_dotenv
import os
import pandas as pd
import datetime
from datetime import date, datetime, timedelta
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import numpy as np
import pymysql
from typing import List
import re
import requests
from fastapi.responses import JSONResponse
###########################################################################

load_dotenv()

#uvicorn main:app --host 0.0.0.0 --port 800 --reload
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:444",
    "https://tufanvpn.dyndns-ip.com",
    "http://tufanvpn.dyndns-ip.com",
    "https://tufanvpn.dyndns-ip.com:5000",
    "http://tufanvpn.dyndns-ip.com:5000",
    "http://tufanvpn.dyndns-ip.com:444",
    "https://127.0.0.1:5000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5000/token",
    "https://127.0.0.1:5000/token",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite todas las orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)


# Configuración de JWT
SECRET_KEY = "z7SM49A&wEHBGedidwimbb25xadjimmcxwIdBAQQgdE2Tfz+4caLuc3L1i"  # Usa una clave secreta segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Usa la función find_user_by_email_and_password para verificar las credenciales
    user_dict = find_user_by_email_and_password(form_data.username, form_data.password)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(user_dict)
    # Asegúrate de que 'username' es una columna en tu base de datos y está incluida en el resultado
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        
        data={"sub": user_dict["NOMBRE"]}
    )
    return {"access_token": access_token, "token_type": "bearer"} 



@app.post("/login")
async def login(email: str, key: str): #login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = find_user_by_email_and_password(form_data.username, form_data.password) #find_user_by_email_and_password(email, key) #find_user_by_email_and_password(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.KEY}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



def find_user_by_email_and_password(email: str, password: str):
    conn_str = conectaFox('f:\\inapsis\\_datos\\')
    connection =pyodbc.connect(conn_str)
    cursor = connection.cursor()
    query = "SELECT nombre FROM _usuario WHERE email = ? AND key = ?"
    cursor.execute(query, (email, password))
    user = cursor.fetchone() 
    user_dict=""
    if user:
        columnas = [columna[0] for columna in cursor.description]
        user_dict = dict(zip(columnas, user))
        cursor.close()
        connection.close()
        return user_dict
    
    cursor.close()
    connection.close()
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            #raise credentials_exception
            raise HTTPException(status_code=401, detail="Credenciales no válidas")

        # Aquí puedes añadir lógica adicional, como buscar al usuario en la base de datos
        print(username)
        return username
    except jwt.PyJWTError:
        #raise credentials_exception
        raise HTTPException(status_code=401, detail="Credenciales no válidas")

#@app.get #leer datos
#@app.post #altas
#@app.put #cambios
#@app.delete

@app.get("/") #path(es parametro de @app)
async def root():
    return {"message": "Hello World"}

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class UserCredentials(BaseModel):
    username: str
    password: str

#consulta SQL usando MariaDB
# Configura los parámetros de conexión a la base de datos
def db_config():
    return pymysql.connect(
        host="127.0.0.1",
        user="root" ,
        password="Nq37.321.1",
        database="kaisen",
        port=3307,  # Cambia el puerto si es necesario
        cursorclass=pymysql.cursors.DictCursor
    )

# Función para ejecutar la consulta SQL (MariaDB)
def execute_query(query, params=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params) if params else cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

# Token de Facture (fijo)
CLAVE_ACCESO = "hXIp21Lm5To7iQQLYM2F"
FACTURE_TOKEN = "4b8939e3e2a099d5517554b5add40b5a"
FACTURE_URL = "https://app.facture.com.mx/api/autofactura"

# 🔄 Modelos para recibir desde VFP (sin claveAcceso)
class Partida(BaseModel):
    descripcion: str
    valorUnitario: float
    claveUnidad: str
    claveProdServ: str
    cantidad: int
    objetoImp: str

class TicketInput(BaseModel):
    numTicket: str
    moneda: str
    formaDePago: str
    sucursalId: int
    partidas: list[Partida]

# 🚀 Endpoint FastAPI
@app.post("/enviar-ticket")
def enviar_factura(input_data: TicketInput):
    try:
        # Armar payload para Facture con claveAcceso fija
        payload = {
            "entity": {
                "data": {
                    "claveAcceso": CLAVE_ACCESO,
                    "numTicket": input_data.numTicket,
                    "moneda": input_data.moneda,
                    "formaDePago": input_data.formaDePago,
                    "sucursal": {
                        "id": input_data.sucursalId
                    },
                    "partidas": [partida.dict() for partida in input_data.partidas]
                }
            }
        }

        # Headers requeridos por Facture
        headers = {
            "Authorization": f"Bearer {FACTURE_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Enviar a Facture
        response = requests.post(FACTURE_URL, json=payload, headers=headers)

        # Devolver resultado al cliente (VFP o Postman)
        if response.status_code in [200, 201]:
            return {
                "status": "ok",
                "facture_response": response.json()
            }
        else:
            return {
                "status": "error",
                "code": response.status_code,
                "facture_response": response.text
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
def get_almacen(_almacen: str) -> str:
    _almacen = _almacen.strip()
    conn_str = conectaFox('f:\\inapsis\\material\\datos\\')
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
    cursor.execute("SELECT almacen FROM ALMACEN WHERE stik = ? LIMIT 1", _almacen)
    resultados = [dict(zip([columna[0] for columna in cursor.description], fila)) for fila in cursor.fetchall()]

    connection.close()
  
    if resultados:
        almacen = resultados[0]["ALMACEN"]
        _path = "f:\\inapsis\\material\\_"
        _fullpath = f"{_path}{almacen}\\"
        return almacen
    else: 
        almacen = None
    
# 🔎 Función reutilizable (fuera del endpoint)
def get_ticket(tabla: str, documen: str):
    _tabla = tabla
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            sql = f"SELECT * FROM `{_tabla}` WHERE documen = %s"
            cursor.execute(sql, (documen,))
            row = cursor.fetchone()
            return row if row else None
    finally:
        conn.close()

    return resultados

# 🔎 Función reutilizable (fuera del endpoint)

def get_ticket_d(tabla: str, documen: str):
    _tabla = tabla
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            #sql = f"SELECT * FROM `{_tabla}` WHERE documen = %s"
            sql = f"SELECT `{_tabla}`.documen,CONCAT_WS(' ', `{_tabla}`.producto, `{_tabla}`.despro, `{_tabla}`.medidas) as descripcio, gp.ccodigosat AS codigosat,`{_tabla}`.n as cantidad,`{_tabla}`.precio, `{_tabla}`.importe FROM `{_tabla}` INNER JOIN gproducto as gp ON `{_tabla}`.producto=gp.producto1 WHERE documen = %s"
            cursor.execute(sql, (documen,))
            row = cursor.fetchall()
            return row if row else None
    finally:
        conn.close()

    return resultados

# 🔎 Función reutilizable (fuera del endpoint)
def get_pago_tik(tabla: str, documen: str):
    _tabla = tabla
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            sql = f"SELECT * FROM `{_tabla}` WHERE documen = %s"
            cursor.execute(sql, (documen,))
            row = cursor.fetchall()
            return row if row else None
    finally:
        conn.close()

    return resultados
#consulta SQL usando ODBC (directo de las tablas DBF)
#@app.get("/empresitas")
#async def obtener_datos(usuario: str = Depends(get_current_user)):
#    try:
#        conn_str=conectaFox('f:\\inapsis\\material\\datos\\')
#        connection = pyodbc.connect(conn_str)
#        cursor = connection.cursor()
#        cursor.execute(f"SELECT * FROM empresitas")
#        columnas = [columna[0] for columna in cursor.description]
#        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
#        #print(resultados)
#        rows = cursor.fetchall()
#        return {"data": resultados}
#    except Exception as e:
#      raise HTTPException(status_code=500, detail=str(e))
#
#    finally:
#        if connection:
#            connection.close()

def cargar_datos():      
    conexion = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Nq37.321.1',
        database='kaisen',
        port=3307
    )

    df_gspock = pd.read_sql("SELECT * FROM gspock WHERE hm > 0;", conexion)
    df_almacenes = pd.read_sql("SELECT * FROM almacenes;", conexion)
    df_gproducto = pd.read_sql("SELECT * FROM gproducto;", conexion)

    conexion.close()

    return df_gspock, df_almacenes, df_gproducto

########################################################################################################################################################################
##################################################################FUNCIONES#############################################################################################
########################################################################################################################################################################
#Obtiene el acceso a la base de datos del almacen seleccionado
def obtener_almacen(_almacen: str) -> str:
    _almacen = _almacen.strip()
    conn_str = conectaFox('f:\\inapsis\\material\\datos\\')
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
    cursor.execute("SELECT CEMP FROM ALMACEN WHERE almacen = ? LIMIT 1", _almacen)
    resultados = [dict(zip([columna[0] for columna in cursor.description], fila)) for fila in cursor.fetchall()]

    connection.close()
  
    if resultados:
        almacen = resultados[0]["CEMP"]
        _path = "f:\\inapsis\\material\\_"
        _fullpath = f"{_path}{almacen}\\"
        return _fullpath
    else: 
        _fullpath = None

    return _fullpath
   

#Obtiene el acceso a la base de datos de la empresa seleccionada (facturacion)
def obtener_empresa(_empresa: str) -> str:
    _empresa = _empresa.strip()
    print(_empresa)
    conn_str = conectaFox('f:\\inapsis\\factura\\datos\\')
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cemp WHERE clave = ? LIMIT 1", _empresa)
    resultados = [dict(zip([columna[0] for columna in cursor.description], fila)) for fila in cursor.fetchall()]

    connection.close()
  
    if resultados:
        empresa = resultados[0]["CLAVE"]
        _t="test"
        _path = "f:\\inapsis\\factura\\"
        _fullpath = f"{_path}{empresa}{_t}\\"
        return _fullpath
    else: 
        _fullpath = None

    return _fullpath
   
