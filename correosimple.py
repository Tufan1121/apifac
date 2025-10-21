import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename
import logging
from urllib.parse import urlencode
import sys

logging.basicConfig(filename='F:\\python\\apidev\\email_errors.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
def enviarEmail(destinatario, asunto, _usuario, _titulo, _documen, _fechayhora, _motivo, _importe, _descuento, _subtotal, _total, _empresa, _kinzd):
    __kind=_kind
    params = urlencode({"empresa": _empresa, "documento": _documen, "kind": __kind})
    _link = "https://tapetestufan.mx/api/auth.html?" + params
    print(_link)
   
    msg = MIMEMultipart()
    html = f"""
        <html lang='en'>
        <head>
        <meta charset='UTF-8'>
        <meta http-equiv='X-UA-Compatible' content='IE=edge'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <link rel='preconnect' href='https://fonts.googleapis.com'>
        <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
        <link href='https://fonts.googleapis.com/css2?family=Quicksand:wght@300;500;700&display=swap' rel='stylesheet'>
        <title>Document</title>
        <style>
            :root {{
                --white: #FFFFFF;
                --black: #000000;
                --very-light-pink: #C7C7C7;
                --text-input-field: #F7F7F7;
                --hospital-green:  #DA0080;
                --sm: 14px;
                --md: 16px;
                --lg: 18px;
            }}
            body {{
                margin: 0;
                font-family: 'Quicksand', sans-serif;
            }}
            .login {{
                width: 100%;
                height: 100vh;
                display: grid;
                place-items: center;
            }}
            .form-container {{
                display: grid;
                grid-template-rows: auto 1fr auto;
                width: 300px;
                justify-items: center;
            }}
            .logo {{
                width: 150px;
                margin-bottom: 48px;
                justify-self: center;
                display: true;
            }}
            .title {{
                font-size: var(--lg);
                margin-bottom: 12px;
                text-align: left;
            }}
            .subtitle {{
                color: var(--very-light-pink);
                font-size: var(--md);
                font-weight: 300;
                margin-top: 0;
                margin-bottom: 14px;
                text-align: left;
            }}
            .email-image {{
                width: 132px;
                height: 132px;
                border-radius: 50%;
                background-color: var(--text-input-field);
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 24px;
            }}
                .email-image img {{
                width: 80px;
            }}
            .resend {{
            font-size: var(--sm);
            }}
            .resend span {{
            color: var(--very-light-pink);
            }}
            .resend a {{
                color: var(--hospital-green);
                text-decoration: none;
            }}
            .primary-button {{
                background-color: var(--hospital-green);
                border-radius: 8px;
                border: none;
                color: var(--white);
                width: 100%;
                cursor: pointer;
                font-size: var(--md);
                font-weight: bold;
                height: 50px;
            }}
            .botonautoriza {{
                display: flex;
                padding: 10px 20px;
                background-color: #DA0080; /* Color de fondo */
                color: white; /* Color del texto */
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                border-radius: 5px; /* Bordes redondeados */
                cursor: pointer; /* Cambiar el cursor a una mano */
                margin-top: 14px;
                margin-bottom: 30px;
            }}
            .login-button {{
                margin-top: 14px;
                margin-bottom: 30px;
            }}
            @media (max-width: 640px) {{
                .logo {{
                    display: block;
                }}
            }}
        </style>
        </head>
        <body>
        <div class='login'>
            <div class='form-container'>
            <h1 class='title'>{_titulo} </h1>
            
            <p class='subtitle'>Usuario: <br><b>{_usuario}</b></br></p>
            <p class='subtitle'>Documento: <br><b>{_documen}</b></br></p>
            <p class='subtitle'>Fecha: <br><b>{_fechayhora}</b></br></p>
            <p class='subtitle'>Motivo: <br><b>{_motivo}</b></br></p>
            <p class='subtitle'>Importe: <br><b>{_importe}</b></br></p>
            <p class='subtitle'>Descuento: <br><b>{_descuento}</b></br></p>
            <p class='subtitle'>Total: <br><b>{_total}</b></br></p>

            <h2><a href={_link} class="botonautoriza"><b>Autorizar</b></a></h2>

        
            </div>
        </div>
        </body>
        </html>
        """

    # Configurar los encabezados del correo
    msg['From'] = 'notificaciones@tapetestufan.com'
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Adjuntar el cuerpo del mensaje al correo
    part = MIMEText(html, 'html')
    msg.attach(part)

    # Información del servidor SMTP y la cuenta
    smtp_server = 'mail.tapetestufan.com'
    smtp_port = 587  # o 465 para SSL
    smtp_user = 'notificaciones@tapetestufan.com'
    smtp_password = 'PGNJM3oiIBqLc'

    # Conectar al servidor SMTP
    try:
        logging.info(f"Iniciando envío de correo a {destinatario}")
        server = smtplib.SMTP(smtp_server, smtp_port)
    except Exception as e:
        logging.error(f"Error al iniciar sesion: {e}")
        # Re-raise the exception if you want the caller to handle it as well.
        raise
    # Iniciar TLS para seguridad
    server.starttls()

    # Autenticarse en el servidor
    server.login(smtp_user, smtp_password)

    # Enviar el correo
    try:
        logging.info(f"Enviando correo a {destinatario}")
        server.send_message(msg)
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario}: {e}")
        # Re-raise the exception if you want the caller to handle it as well.
        raise    

    # Cerrar la conexión
    server.quit()

    if __name__ == "__main__":
        logging.info(f"Argumentos recibidos: {sys.argv[1:]}")

        destinatario = sys.argv[1]
        asunto       = sys.argv[2]
        _usuario     = sys.argv[3]
        _titulo      = sys.argv[4]
        _documen     = sys.argv[5]
        _fechayhora  = sys.argv[6]
        _motivo      = sys.argv[7]
        _importe     = sys.argv[8]
        _descuento   = sys.argv[9]
        _subtotal    = sys.argv[10]
        _total       = sys.argv[11]
        _empresa     = sys.argv[12]        
        _kind        = sys.argv[13]
            
        enviarEmail(destinatario, asunto, _usuario, _titulo, _documen, _fechayhora, _motivo, _importe, _descuento, _subtotal, _total, _empresa, _kind)
