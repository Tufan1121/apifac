from fastapi import FastAPI, Query, HTTPException, status, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt
from database import conectaFox  # Importa la función de tu otro script
from database import conectaMaria  # Importa la función de tu otro script
from correo import enviarEmail
from correocotiza import enviarEmailCot, enviarEmailSimple
from enum import Enum
from typing import Any, Optional, Union, List, Annotated
from pydantic import BaseModel, condecimal, field_validator, model_validator
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
from defusedxml.ElementTree import fromstring as safe_fromstring 
from base64 import b64decode
import re
from defusedxml.ElementTree import fromstring as safe_fromstring  # asegúrate de este import
from zoneinfo import ZoneInfo
from pypdf import PdfReader
from io import BytesIO
###########################################################################

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
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT", 3307)),
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

def decode_xml_b64(b64: str) -> str:
    # Permite base64 con saltos/espacios
    normalized = re.sub(r"\s+", "", b64 or "")
    raw = b64decode(normalized, validate=False)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        # Último recurso: reemplaza caracteres inválidos
        return raw.decode("utf-8", "replace")

def normalize_xml_whitespace(s: Optional[str]) -> Optional[str]:
    if not isinstance(s, str):
        return s
    # quita controles no válidos en XML 1.0 (excepto \t \n \r)
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", s)
    return s.strip()

def quitar_saltos_de_pagina(xml: str) -> str:
    # elimina form feed (\x0c) y separadores Unicode de línea/párrafo
    xml = re.sub(r'[\x0c\u2028\u2029]', '', xml)
    # opcional: si también quieres quitar CR/LF para dejarlo en una sola línea:
    # xml = xml.replace('\r', '').replace('\n', '')
    return xml

class FacturaPayload(BaseModel):
    erfc:     str
    sucursal: str
    serie:    str
    folio:    str
    subtotal: condecimal(max_digits=15, decimal_places=4)
    impuesto: condecimal(max_digits=15, decimal_places=4)
    total:    condecimal(max_digits=15, decimal_places=4)
    uuid:     str
    rrfc:     str
    rnombre:  str
    ruso:     str
    rregimen: str
    rcp:      str
    tickets:  str
    fecha:  datetime
    servicio: str
    # acepta XML en texto plano o en base64
    xml_cfdi: Optional[str] = None
    xml_cfdi_b64: Optional[str] = None

     # ✅ 1) Pobla xml_cfdi desde xml_cfdi_b64 ANTES de validar campos
    @model_validator(mode="before")
    @classmethod
    def populate_xml_from_b64(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("xml_cfdi") and data.get("xml_cfdi_b64"):
                try:
                    data["xml_cfdi"] = decode_xml_b64(data["xml_cfdi_b64"])
                except Exception as e:
                    raise ValueError(f"xml_cfdi_b64 inválido: {e}")
        return data

    # ✅ 2) Normaliza whitespace problemático en el XML ya decodificado
    @field_validator("xml_cfdi", mode="before")
    @classmethod
    def normalize_before_validate(cls, v: Optional[str]):
        return normalize_xml_whitespace(v) if isinstance(v, str) else v

    # ✅ 3) Verifica que sea XML bien formado (y seguro)
    @field_validator("xml_cfdi")
    @classmethod
    def validar_xml(cls, v: Optional[str]):
        if v is None:
            return v
        safe_fromstring(v)  # lanza si no es XML válido
        return v

    # ✅ 4) Reglas de presencia
    @model_validator(mode="after")
    def require_one_xml(self):
        if not (self.xml_cfdi or self.xml_cfdi_b64):
            raise ValueError("Debes enviar 'xml_cfdi' (texto) o 'xml_cfdi_b64' (base64).")
        return self

    """
    @field_validator("xml_cfdi", mode="before")
    @classmethod
    def normalize_before_validate(cls, v: str):
        # Evita “Invalid control character at …”
        return normalize_xml_whitespace(v)

    @field_validator("xml_cfdi")
    @classmethod
    def validar_xml(cls, v: str):
        # Valida que sea XML bien formado (sin XXE)
        safe_fromstring(v)
        return v
    """
    #def validar_xml(cls, v: str):
    #    try:
            # No hace falta encode; acepta str
    #        safe_fromstring(v)
    #    except Exception as e:
    #       raise ValueError(f"XML inválido: {e}")
    #   return v

# 3) Endpoint protegido que recibe el JSON y el usuario actual
@app.post("/recibefacturas/")
async def actualizar_factura(factura: FacturaPayload, usuario: str = Depends(get_current_user)):
    """
    Inserta una nueva fila en kaisen.brfac con TODOS los campos obligatorios.
    """
    conn = db_config()
    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO brfac
              (erfc, sucursal, serie, folio,
               subtotal, impuesto, total,
               uuid, rrfc, rnombre, ruso,
               rregimen, rcp, tickets, fecha, servicio, xml_cfdi)
            VALUES
             (%s, %s, %s, %s,
              %s, %s, %s,
              %s, %s, %s, %s,
              %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                factura.erfc,
                factura.sucursal,
                factura.serie,
                factura.folio,
                factura.subtotal,
                factura.impuesto,
                factura.total,
                factura.uuid,
                factura.rrfc,
                factura.rnombre,
                factura.ruso,
                factura.rregimen,
                factura.rcp,
                json.dumps(factura.tickets),  # 👈 convierte lista a JSON string
                factura.fecha,
                factura.servicio,
                factura.xml_cfdi
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al insertar factura: {e}"
        )
    finally:
        conn.close()

    return {
        "msg": f"Factura {factura.uuid} insertada",
        "datos": factura.dict()
    }

def obtener_prefijo(cadena):
    match = re.match(r'^([A-Za-z]+)', cadena)
    if match:
        return match.group(1)
    return None

def get_numbers(cadena):
    match = re.match(r'^(\d+)', cadena)
    if match:
        return match.group(1)
    return None

class DocumentoPayload(BaseModel):
    ticket: str

@app.post("/tickets")
async def tickets(factura: DocumentoPayload, usuario: str = Depends(get_current_user)):
    _documen = factura.ticket
    _prefijo = obtener_prefijo(_documen)
    _almacen = get_almacen(_prefijo)

    if not _prefijo or not _almacen:
        return {"error": "Ticket no existe"}

    _pos = f"pos{_almacen}"
    _posed = f"posed{_almacen}"
    _pagofac = f"pospago{_almacen}"

    # 1) Intentar obtener el ticket y capturar la excepción interna si la hay
    try:
        resultado = get_ticket(_pos, _documen)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no existe")

    # 2) Si devuelve None o está vacío
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no existe")

    estado_ticket = resultado.get("estado")
    fecha_ticket = resultado.get("fecha")
    _rfc=resultado.get("rfc")
    print("fecha",fecha_ticket)

    # Normalizar a datetime
    if isinstance(fecha_ticket, datetime):
        dt_ticket = fecha_ticket
    elif isinstance(fecha_ticket, date):
        dt_ticket = datetime(fecha_ticket.year, fecha_ticket.month, fecha_ticket.day)
    elif isinstance(fecha_ticket, str):
        # Ajusta el formato si tu columna 'crea' viene en otro formato
        # Ejemplos comunes: "%Y-%m-%d %H:%M:%S" o "%Y-%m-%d"
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt_ticket = datetime.strptime(fecha_ticket, fmt)
                break
            except ValueError:
                dt_ticket = None
        if dt_ticket is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de fecha inválido en ticket")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de fecha de ticket no soportado")

    # Hora del sistema en Zona Horaria de México (CDMX)
    ahora = datetime.now(ZoneInfo("America/Mexico_City"))
    
    if (dt_ticket.year != ahora.year) or (dt_ticket.month != ahora.month) and _rfc != "XAXX010101000":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ticket ya no es facturable este mes"
        )
    
    if estado_ticket == 2 and _rfc != "XAXX010101000":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket facturado")
    elif estado_ticket == 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket cancelado")

    

    _detalle = get_ticket_d(_posed, _documen)
    _pago = get_pago_tik(_pagofac, _documen)
    
    # Valida que el ticket no este siendo ocupado en otra sesion

    # 3) Devolver un único dict para evitar que FastAPI lo interprete mal
    
    _busy=lock_ticket_if_free(_pos,_documen)
    print("esta ocupado",_busy)

    if _busy.get("ok") and not _busy.get("acquired"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ticket no disponible por el momento"
        )
    elif _busy.get("ok") and _busy.get("acquired"):
        print("✅ Lock adquirido correctamente.")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    

    print("sucursal", _almacen)
    print("ticket",resultado)
    print("detalle", _detalle)
    print("pago", _pago)
        
    return {
        "sucursal": _almacen,
        "ticket": resultado,
        "detalle": _detalle,
        "pago": _pago
    }

@app.post("/ticket_estado")
async def tickets(factura: DocumentoPayload, usuario: str = Depends(get_current_user)):
    _documen = factura.ticket
    _prefijo = obtener_prefijo(_documen)
    _almacen = get_almacen(_prefijo)

    if not _prefijo or not _almacen:
        return {"error": "Ticket no existe"}

    _pos = f"pos{_almacen}"
    _posed = f"posed{_almacen}"
    _pagofac = f"pospago{_almacen}"

    # 1) Intentar obtener el ticket y capturar la excepción interna si la hay
    try:
        resultado = get_ticket(_pos, _documen)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no existe")

    # 2) Si devuelve None o está vacío
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no existe")

    estado_ticket = resultado.get("estado")
    fecha_ticket = resultado.get("fecha")
    _rfc = resultado.get("rfc")
    print("fecha",fecha_ticket)
    
    if estado_ticket == 2 and _rfc != "XAXX010101000":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket facturado")
    elif estado_ticket == 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket cancelado")
    elif estado_ticket == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket Libre")


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
    
# ================================
# 🔎 Consulta (tu función existente)
# ================================
def get_ticket(tabla: str, documen: str):
    _tabla = tabla
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            sql = f"""
                SELECT TRIM(documen) as noVenta,
                       crea as fecha,
                       (total-impuesto) as subtotal,
                       impuesto,
                       total,
                       estado,
                       rfc,
                       lock_owner,
                       lock_until,
                       TIMESTAMPDIFF(SECOND, NOW(), lock_until) AS ttl_seconds
                FROM `{_tabla}`
                WHERE documen = %s
            """
            cursor.execute(sql, (documen,))
            row = cursor.fetchone()
            return row if row else None
    finally:
        conn.close()

# 🔎 Función reutilizable (fuera del endpoint)

def get_ticket_d(tabla: str, documen: str):
    _tabla = tabla
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            #sql = f"SELECT * FROM `{_tabla}` WHERE documen = %s"
            #sql = f"SELECT `{_tabla}`.documen,CONCAT_WS(' ', `{_tabla}`.producto, `{_tabla}`.despro, `{_tabla}`.medidas) as descripcio, gp.ccodigosat AS codigosat,`{_tabla}`.n as cantidad,`{_tabla}`.precio, `{_tabla}`.importe FROM `{_tabla}` INNER JOIN gproducto as gp ON `{_tabla}`.producto=gp.producto1 WHERE documen = %s"
            sql = f"SELECT gp.ccodigosat AS claveproducto, TRIM(CONCAT_WS(' ', `{_tabla}`.producto, `{_tabla}`.despro, TRIM(gp.diseno),`{_tabla}`.medidas)) as descripcio,gp.cunidad AS claveunidad,`{_tabla}`.n as cantidad,`{_tabla}`.precio, `{_tabla}`.importe FROM `{_tabla}` left JOIN gproducto as gp ON `{_tabla}`.producto1=gp.producto WHERE documen = %s"
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
            sql = f"SELECT LEFT(TRIM(pago), 2) AS formapago FROM `{_tabla}` WHERE documen = %s GROUP BY pago ORDER by cantidad desc LIMIT 1"

            cursor.execute(sql, (documen,))
            row = cursor.fetchone()
            
            if not row:
                return None

            # Si el cursor devuelve tuplas, conviértelo a dict:
            if not isinstance(row, dict):
                cols = [c[0] for c in cursor.description]
                row = dict(zip(cols, row))

            return row  # <-- dict como {"formapago": "04"}
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
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Nq37.321.1"),
        database=os.getenv("DB_DATABASE", "kaisen"),
        port=int(os.getenv("DB_PORT", 3307))
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
   
#Correo Simple
@app.post("/simplem")
async def sendm(destinatario: str, asunto: str, _usuario: str, _titulo: str,_titulo1: str,_titulo2: str, s_link: str = None, _attachment: str = None):
    print(_attachment)
    if _attachment:
        enviarEmailSimplenol(destinatario, asunto, _usuario, _titulo,_titulo1,_titulo2, s_link, _attachment)
    else:
        enviarEmailSimplenol(destinatario, asunto, _usuario, _titulo,_titulo1,_titulo2, s_link)


from typing import Optional, Dict, Any
import uuid

# ================================
# 🔒 Lock: adquirir/renovar si está libre
# ================================
def lock_ticket_if_free(tabla: str, documen: str, owner: Optional[str] = None, ttl_minutes: int = 15) -> Dict[str, Any]:
    """
    Intenta adquirir el lock de un ticket por 'ttl_minutes'.
    - Si no hay lock o está vencido → lo toma y devuelve acquired=True.
    - Si está bloqueado por el mismo owner → renueva y devuelve acquired=True, renewed=True.
    - Si está bloqueado por otro → acquired=False y devuelve ttl_seconds restantes.
    """
    if owner is None:
        owner = str(uuid.uuid4())

    conn = db_config()
    try:
        with conn.cursor() as cursor:
            # 1) Leer estado actual del lock
            sql_get = f"""
                SELECT lock_owner,
                       lock_until,
                       TIMESTAMPDIFF(SECOND, NOW(), lock_until) AS ttl_seconds
                FROM `{tabla}`
                WHERE documen = %s
            """
            cursor.execute(sql_get, (documen,))
            row = cursor.fetchone()

            if not row:
                return {"ok": False, "error": "NOT_FOUND", "message": "El ticket no existe."}

            lock_owner, lock_until, ttl_seconds = row

            # Convertir ttl_seconds a int de forma segura
            if ttl_seconds is not None:
                try:
                    ttl_seconds = int(ttl_seconds)
                except (ValueError, TypeError):
                    ttl_seconds = 0
            else:
                ttl_seconds = 0

            # 2) Si está libre o vencido → tomar lock de forma atómica
            if (lock_until is None) or (ttl_seconds <= 0):
                sql_lock = f"""
                    UPDATE `{tabla}`
                    SET lock_owner = %s,
                        lock_until = DATE_ADD(NOW(), INTERVAL %s MINUTE)
                    WHERE documen = %s
                      AND (lock_until IS NULL OR lock_until < NOW())
                """
                cursor.execute(sql_lock, (owner, ttl_minutes, documen))
                affected = cursor.rowcount
                conn.commit()

                if affected == 1:
                    # Lock adquirido
                    return {
                        "ok": True,
                        "acquired": True,
                        "renewed": False,
                        "owner": owner,
                        "ttl_seconds": ttl_minutes * 60
                    }

                # Otro proceso se adelantó: releer y reportar estado
                cursor.execute(sql_get, (documen,))
                row2 = cursor.fetchone()
                if not row2:
                    return {"ok": False, "error": "NOT_FOUND"}
                lock_owner2, lock_until2, ttl_seconds2 = row2
                try:
                    ttl_seconds2 = int(ttl_seconds2) if ttl_seconds2 is not None else 0
                except (ValueError, TypeError):
                    ttl_seconds2 = 0
                return {
                    "ok": True,
                    "acquired": False,
                    "owner": lock_owner2,
                    "ttl_seconds": max(0, ttl_seconds2)
                }

            # 3) Ya está bloqueado y no ha expirado
            if lock_owner == owner:
                # Renovar TTL (heartbeat)
                sql_renew = f"""
                    UPDATE `{tabla}`
                    SET lock_until = DATE_ADD(NOW(), INTERVAL %s MINUTE)
                    WHERE documen = %s
                      AND lock_owner = %s
                      AND lock_until > NOW()
                """
                cursor.execute(sql_renew, (ttl_minutes, documen, owner))
                conn.commit()
                return {
                    "ok": True,
                    "acquired": True,
                    "renewed": True,
                    "owner": owner,
                    "ttl_seconds": ttl_minutes * 60
                }

            # 4) Bloqueado por otro owner
            return {
                "ok": True,
                "acquired": False,
                "owner": lock_owner,
                "ttl_seconds": max(0, ttl_seconds)
            }

    finally:
        conn.close()


# ================================
# 🔁 Heartbeat: renovar si eres el dueño
# ================================
def refresh_ticket_lock(tabla: str, documen: str, owner: str, ttl_minutes: int = 15) -> Dict[str, Any]:
    """
    Renueva el lock si:
      - lock_owner coincide con 'owner'
      - el lock no ha expirado
    """
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            sql = f"""
                UPDATE `{tabla}`
                SET lock_until = DATE_ADD(NOW(), INTERVAL %s MINUTE)
                WHERE documen = %s
                  AND lock_owner = %s
                  AND lock_until > NOW()
            """
            cursor.execute(sql, (ttl_minutes, documen, owner))
            affected = cursor.rowcount
            conn.commit()

            if affected == 1:
                return {"ok": True, "renewed": True, "ttl_seconds": ttl_minutes * 60}

            # Si no renovó, informar por qué
            sql_get = f"""
                SELECT lock_owner,
                       lock_until,
                       TIMESTAMPDIFF(SECOND, NOW(), lock_until) AS ttl_seconds
                FROM `{tabla}`
                WHERE documen = %s
            """
            cursor.execute(sql_get, (documen,))
            row = cursor.fetchone()
            if not row:
                return {"ok": False, "renewed": False, "error": "NOT_FOUND"}

            lock_owner, lock_until, ttl_seconds = row
            try:
                ttl_seconds = int(ttl_seconds) if ttl_seconds is not None else 0
            except (ValueError, TypeError):
                ttl_seconds = 0

            if lock_owner != owner:
                return {"ok": False, "renewed": False, "error": "NOT_OWNER", "ttl_seconds": max(0, ttl_seconds)}
            return {"ok": False, "renewed": False, "error": "EXPIRED", "ttl_seconds": 0}
    finally:
        conn.close()


# ================================
# 🧼 Liberar: al facturar o cancelar
# ================================
def release_ticket_lock(tabla: str, documen: str, owner: str) -> Dict[str, Any]:
    """
    Libera el lock sólo si 'owner' es quien lo tiene.
    """
    conn = db_config()
    try:
        with conn.cursor() as cursor:
            sql = f"""
                UPDATE `{tabla}`
                SET lock_owner = NULL,
                    lock_until = NULL
                WHERE documen = %s
                  AND lock_owner = %s
            """
            cursor.execute(sql, (documen, owner))
            affected = cursor.rowcount
            conn.commit()
            return {"ok": True, "released": affected == 1}
    finally:
        conn.close()

#############################################
#####EXTRAE INFORMACION DE LA CONSTANCIA#####
#############################################
def pdf_to_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n".join((p.extract_text() or "") for p in reader.pages)

def normalize(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def extract_field(pattern: str, text: str):
    m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else None

def extract_regimenes(text: str):
    regimenes = []

    block = re.search(
        r"Regímenes:\s*\n(.*?)(?:\nObligaciones:|\nActividades|\Z)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not block:
        return regimenes

    for line in block.group(1).splitlines():
        line = line.strip()
        if not line:
            continue

        # Quita fechas dd/mm/aaaa
        line = re.sub(r"\d{2}/\d{2}/\d{4}", "", line).strip()
        low = line.lower()

        # Quita encabezados tipo: "Régimen Fecha Inicio Fecha Fin"
        if "fecha inicio" in low or "fecha fin" in low:
            continue
        if low in ("régimen", "regimen"):
            continue

        # Acepta líneas que contienen el texto del régimen
        # (en tus PDFs vienen como "Régimen de ..." o "Régimen General ...")
        if low.startswith("régimen") or low.startswith("regimen"):
            regimenes.append(line)

    # Dedup conservando orden
    seen = set()
    out = []
    for r in regimenes:
        key = r.lower()
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out

def extract_razon_social(text: str):
    # Persona moral
    rs = extract_field(r"Denominación/Razón Social:\s*([^\n]+)", text)
    if rs:
        return rs

    # Persona física (arma nombre completo)
    nombre = extract_field(r"Nombre\s*\(s\):\s*([^\n]+)", text)
    ap1 = extract_field(r"Primer Apellido:\s*([^\n]+)", text)
    ap2 = extract_field(r"Segundo Apellido:\s*([^\n]+)", text)

    parts = [p for p in [nombre, ap1, ap2] if p]
    return " ".join(parts) if parts else None

def x(s: str) -> str:
    return html.escape(s or "")

@app.post("/csf/extract")
async def extract_csf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    # Seguridad mínima (sin guardar a disco)
    if not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(400, "Archivo no es un PDF válido")
    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise HTTPException(413, "PDF demasiado grande")

    text = normalize(pdf_to_text(pdf_bytes))
    if not text:
        raise HTTPException(422, "PDF sin texto (escaneado)")

    return {
        "ok": True,
        "data": {
            "rfc": extract_field(r"RFC:\s*([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})", text),
            "razon_social": extract_razon_social(text),
            "codigo_postal": extract_field(r"Código Postal:\s*([0-9]{5})", text),
            "regimenes": extract_regimenes(text),
        },
    }