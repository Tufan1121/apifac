import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename
import sys

def enviar_correo(destinatarios_str, asunto, mensaje, _attachment :str = None):
    # Divide la cadena de destinatarios en una lista
    destinatarios = destinatarios_str.split(';')
    
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
            <h1 class='title'>{mensaje} </h1>        
            </div>
        </div>
        </body>
        </html>
    """
    # Inicia el mensaje
    msg = MIMEMultipart()
    msg['From'] = 'notificaciones@tapetestufan.com'
    msg['To'] = ', '.join(destinatarios)  # Convierte la lista de nuevo en una cadena para el campo 'To'
    msg['Subject'] = asunto
    
    # Adjunta el cuerpo del mensaje en HTML
    part = MIMEText(html, 'html')
    msg.attach(part)
    if _attachment:
        with open(_attachment, "rb") as f:
            part = MIMEApplication(f.read(), Name=basename(_attachment))
            # Agregar un 'content-disposition' al adjunto, si lo deseas
            part['Content-Disposition'] = f'attachment; filename="{basename(_attachment)}"'
            msg.attach(part)
    # Configuración del servidor SMTP
    servidor_smtp = "mail.tapetestufan.com"
    puerto = 587
    smtp_user = 'notificaciones@tapetestufan.com'
    smtp_password = 'PGNJM3oiIBqLc'
    
    # Conectar al servidor y enviar el correo
    server = smtplib.SMTP(servidor_smtp, puerto)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, destinatarios, msg.as_string())  # Asegúrate de pasar la lista de destinatarios aquí
    server.quit()

if __name__ == "__main__":
    # Asegúrate de que se pasan los argumentos correctamente
    if len(sys.argv) < 4:
        print("Uso: script.py 'destinatario1;destinatario2' 'Asunto' 'Mensaje'")
    else:
        destinatarios_str = sys.argv[1]
        asunto = sys.argv[2]
        mensaje = sys.argv[3]
        _attachment = sys.argv[4] if len(sys.argv) > 4 else None
        enviar_correo(destinatarios_str, asunto, mensaje, _attachment)
