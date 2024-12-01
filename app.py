from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os

from datetime import datetime
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Ruta base donde se almacenarán las carpetas
BASE_UPLOAD_FOLDER = 'archivos/'
PRESUPUESTO_UPLOAD_FOLDER = 'presupuestos/'

# Endpoint para subir archivos
@app.route('/presupuesto', methods=['POST'])
def upload_file():
    folder_name = request.form.get('folder_name')
    
    if not folder_name:
        return jsonify({"error": "No folder name provided"}), 400
    
    # Ruta para la primera carpeta
    folder_path = os.path.join(BASE_UPLOAD_FOLDER, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Crear carpeta si no existe
    
    # Guardar archivo en la primera carpeta
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    new_filename = folder_name + '.pdf'
    filepath = os.path.join(folder_path, new_filename)
    
    file.save(filepath)

    # Obtener la fecha actual para la segunda carpeta
    fecha_actual = datetime.now()
    folder_presupuesto = f"{fecha_actual.year}/{fecha_actual.month}"
    folder_pathPresupuesto = os.path.join(PRESUPUESTO_UPLOAD_FOLDER, folder_presupuesto)
    
    if not os.path.exists(folder_pathPresupuesto):
        os.makedirs(folder_pathPresupuesto)  # Crear carpeta si no existe
    
    # Guardar archivo en la segunda carpeta
    filepathPresupuesto = os.path.join(folder_pathPresupuesto, new_filename)
    
    # Copiar archivo a la segunda carpeta
    file.seek(0)  # Volver al principio del archivo
    with open(filepathPresupuesto, 'wb') as f:
        f.write(file.read())
    
    return jsonify({"message": f"File successfully uploaded to {filepath} and {filepathPresupuesto}"}), 200

# Endpoint para enviar correos
@app.route('/send-email', methods=['POST'])
def send_email():
    mail_content = request.form.get('text', '')
    subject = request.form.get('subject', 'No Subject')
    receiver_address = request.form.get('to', '')  # Dirección del destinatario
    bcc_address = 'informesmedicospericiales@gmail.com'
    firma_html = """
    <div class="default-style">
        <img id="0e70ed49-e52c-4efd-ac95-eab14cbbcb5b" class="aspect-ratio" style="max-width: 100%; display: block; margin-left: auto; margin-right: auto;" src="/appsuite/api/image/mail/picture?folder=default0%2FElementos+enviados&amp;id=1732959057263756228&amp;uid=0e70ed49-e52c-4efd-ac95-eab14cbbcb5b" alt="" width="362" height="121">
    </div>
    """
    
    # Concatena el contenido del correo con la firma HTML
    mail_content_con_firma = f"{mail_content}{firma_html}"
    host = 'smtp.ionos.es'
    port = 587
    sender_address = 'info@informesmedicospericiales.com'  # Dirección de correo IONOS
    sender_password = 'rrpy1Jf7OKvOnEu'  # Contraseña de correo IONOS

    # Crear el mensaje del correo
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject

    # Adjuntar el cuerpo del correo
    # message.attach(MIMEText(mail_content, 'plain'))
    message.attach(MIMEText(mail_content_con_firma, 'html'))
    # Verificar si se incluye un archivo adjunto
    if 'file' in request.files:
        file = request.files['file']
        file_name = file.filename

        # Leer el archivo adjunto
        attachment = file.read()

        # Crear el adjunto MIMEBase
        attach = MIMEBase('application', 'octet-stream')
        attach.set_payload(attachment)

        # Codificar el adjunto en Base64
        encoders.encode_base64(attach)

        # Agregar encabezado con el nombre del archivo
        attach.add_header('Content-Disposition', f'attachment; filename= {file_name}')

        # Adjuntar el archivo al mensaje
        message.attach(attach)

    try:
        # Configurar la sesión SMTP
        session = smtplib.SMTP(host, port)
        session.starttls()  # Iniciar TLS
        session.login(sender_address, sender_password)
        envio = [receiver_address]
        if bcc_address:
            envio.append(bcc_address)
        # Enviar el correo
        session.sendmail(sender_address, envio, message.as_string())
        session.quit()

        return jsonify({"message": "Email sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     if not os.path.exists(BASE_UPLOAD_FOLDER):
#         os.makedirs(BASE_UPLOAD_FOLDER)  # Crear la carpeta base si no existe
if __name__ == '__main__':
    if not os.path.exists(BASE_UPLOAD_FOLDER):
        os.makedirs(BASE_UPLOAD_FOLDER)  # Crear la carpeta base si no existe
    if not os.path.exists(PRESUPUESTO_UPLOAD_FOLDER):
        os.makedirs(PRESUPUESTO_UPLOAD_FOLDER)  # Crear la carpeta base para presupuestos si no existe


    app.run(host='0.0.0.0', port=8001, debug=True)
