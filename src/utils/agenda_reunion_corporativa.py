import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import pygsheets
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

class AgendaReunionCorporativa:
    
    def __init__(self):
        # Configuración desde variables de entorno (usando las mismas variables que ya funcionan)
        self.corporate_email = os.getenv("EMAIL_REMITENTE", "kevin.inofuente.colque.27@gmail.com")  # Mismo email para todo
        self.email_user = os.getenv("EMAIL_REMITENTE")  # EMAIL_REMITENTE en lugar de EMAIL_USER
        self.email_password = os.getenv("APP_PASSWORD_GMAIL")  # APP_PASSWORD_GMAIL en lugar de EMAIL_PASSWORD
        self.timezone = os.getenv("TIMEZONE", "America/Lima")
        
    def obtener_fecha_hora_actual(self):
        """Obtiene la fecha y hora actual en la zona horaria configurada"""
        try:
            tz = pytz.timezone(self.timezone)
            ahora = datetime.now(tz)
            
            # Formatear para mostrar al usuario
            dia_actual = ahora.strftime("%A %d de %B, %Y")
            hora_actual = ahora.strftime("%I:%M %p")
            
            # Traducir días al español
            dias_es = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            
            meses_es = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            
            # Reemplazar nombres en español
            for eng, esp in dias_es.items():
                dia_actual = dia_actual.replace(eng, esp)
            for eng, esp in meses_es.items():
                dia_actual = dia_actual.replace(eng, esp)
                
            return {
                'fecha_actual': dia_actual,
                'hora_actual': hora_actual,
                'timestamp': ahora
            }
        except Exception as e:
            print(f"❌ Error obteniendo fecha/hora: {e}")
            return None
    
    def validar_fecha_reunion(self, fecha_reunion, hora_reunion):
        """Valida que la fecha y hora de reunión sean válidas"""
        try:
            # Obtener fecha actual
            info_actual = self.obtener_fecha_hora_actual()
            if not info_actual:
                return False, "Error obteniendo fecha actual"
            
            # Aquí podrías agregar validaciones más específicas
            # Por ejemplo: no permitir fines de semana, horarios de oficina, etc.
            
            return True, "Fecha válida"
            
        except Exception as e:
            return False, f"Error validando fecha: {e}"
    
    def crear_evento_google_calendar(self, nombre_contacto, empresa, correo, fecha_reunion, hora_reunion):
        """Crea un evento real en Google Calendar"""
        try:
            # Obtener credenciales de la cuenta de servicio
            service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
            print(f"🔍 DEBUG: Service account path: {service_account_path}")
            
            if not service_account_path or not os.path.exists(service_account_path):
                print("❌ Error: Archivo de credenciales de Google no encontrado")
                return False, "Archivo de credenciales no encontrado"
            
            print(f"✅ Archivo de credenciales encontrado: {service_account_path}")
            
            # Configurar credenciales para Google Calendar
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            print(f"🔍 DEBUG: Intentando autenticar con scopes: {SCOPES}")
            
            credentials = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
            print(f"✅ Credenciales creadas exitosamente")
            
            service = build('calendar', 'v3', credentials=credentials)
            print(f"✅ Servicio de Google Calendar creado exitosamente")
            
            # Parsear fecha y hora
            try:
                # Intentar parsear la fecha en formato YYYY-MM-DD
                if len(fecha_reunion.split('-')) == 3:
                    fecha_obj = datetime.strptime(fecha_reunion, '%Y-%m-%d')
                else:
                    # Si no está en formato estándar, usar fecha actual + días
                    fecha_obj = datetime.now() + timedelta(days=2)
                
                # Parsear hora (formato HH:MM o H:MM)
                if ':' in hora_reunion:
                    if 'PM' in hora_reunion.upper() or 'AM' in hora_reunion.upper():
                        hora_obj = datetime.strptime(hora_reunion.strip(), '%H:%M %p').time()
                    else:
                        hora_obj = datetime.strptime(hora_reunion.strip(), '%H:%M').time()
                else:
                    # Asumir formato de 24 horas
                    hora_num = int(hora_reunion.replace(':00', ''))
                    hora_obj = datetime.strptime(f"{hora_num}:00", '%H:%M').time()
                
                # Combinar fecha y hora en zona horaria de Lima
                tz = pytz.timezone(self.timezone)
                fecha_hora_inicio = tz.localize(datetime.combine(fecha_obj.date(), hora_obj))
                fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=45)  # Reunión de 45 minutos
                
            except Exception as e:
                print(f"❌ Error parseando fecha/hora: {e}")
                # Fallback: agendar para mañana a las 3 PM
                mañana = datetime.now() + timedelta(days=1)
                tz = pytz.timezone(self.timezone)
                fecha_hora_inicio = tz.localize(datetime.combine(mañana.date(), datetime.strptime("15:00", '%H:%M').time()))
                fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=45)
            
            # Crear evento
            evento = {
                'summary': f'Reunión Corporativa - {empresa}',
                'description': f'''
Reunión de capacitación corporativa con {empresa}

👤 Contacto: {nombre_contacto}
🏢 Empresa: {empresa}
📧 Email: {correo}
🎯 Objetivo: Discutir capacitación en Machine Learning/Data Analytics

Agenda:
- Presentación de DataPath
- Evaluación de necesidades del equipo
- Propuesta de programa personalizado
- Definición de cronograma

Link de reunión: [Se enviará 30 minutos antes]
                ''',
                'start': {
                    'dateTime': fecha_hora_inicio.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': fecha_hora_fin.isoformat(),
                    'timeZone': self.timezone,
                },
                'attendees': [
                    {'email': correo},
                    {'email': self.email_user},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 día antes
                        {'method': 'email', 'minutes': 30},       # 30 minutos antes
                    ],
                },
            }
            
            # Insertar evento en el calendar principal
            print(f"🔍 DEBUG: Intentando crear evento en calendario 'primary'")
            print(f"🔍 DEBUG: Evento a crear: {evento['summary']}")
            
            evento_creado = service.events().insert(calendarId='primary', body=evento).execute()
            print(f"✅ Evento creado en Google Calendar: {evento_creado.get('htmlLink')}")
            return True, evento_creado.get('htmlLink')
            
        except Exception as e:
            print(f"❌ Error creando evento en Google Calendar: {e}")
            return False, str(e)
    
    def generar_mensaje_confirmacion_lead(self, nombre_contacto, empresa, fecha_reunion, hora_reunion):
        """Genera el mensaje de confirmación para el lead"""
        return f"""
¡Hola {nombre_contacto}!

Confirmamos tu solicitud de reunión corporativa para {empresa}.

📅 **Detalles de la reunión:**
• Fecha: {fecha_reunion}
• Hora: {hora_reunion}
• Duración: 30-45 minutos
• Modalidad: Videollamada (te enviaremos el link)

🎯 **En esta reunión hablaremos sobre:**
• Necesidades específicas de capacitación de tu equipo
• Programas personalizados de DataPath
• Cronograma y metodología de implementación
• Propuesta comercial adaptada a tu empresa

Nuestro equipo comercial corporativo se pondrá en contacto contigo en las próximas 2 horas para confirmar los detalles y enviarte el enlace de la reunión.

¡Gracias por confiar en DataPath para la transformación digital de tu equipo!

Saludos cordiales,
Kevin - Consultor DataPath
www.datapath.com
"""

    def generar_mensaje_interno_equipo(self, nombre_contacto, empresa, correo, tamano_equipo, area_capacitacion, fecha_reunion, hora_reunion):
        """Genera el mensaje interno para el equipo comercial"""
        return f"""
🚨 **NUEVA REUNIÓN CORPORATIVA AGENDADA** 🚨

**Lead B2B de alta prioridad:**

👤 **Contacto:** {nombre_contacto}
🏢 **Empresa:** {empresa}
📧 **Email:** {correo}
👥 **Tamaño equipo:** {tamano_equipo} personas
🎯 **Área capacitación:** {area_capacitacion}

📅 **Reunión solicitada:**
• Fecha: {fecha_reunion}
• Hora: {hora_reunion}

⚡ **ACCIONES REQUERIDAS:**
1. Contactar al lead en las próximas 2 horas
2. Confirmar disponibilidad y enviar link de reunión
3. Preparar propuesta personalizada según el tamaño del equipo
4. Asignar account manager corporativo

💰 **Valor estimado:** Potencial contrato para {tamano_equipo} personas

¡Prioridad alta para seguimiento!

---
Generado automáticamente por Kevin (Bot DataPath)
"""

    def enviar_correos(self, nombre_contacto, empresa, correo, tamano_equipo, area_capacitacion, fecha_reunion, hora_reunion):
        """Envía correos de confirmación al lead y notificación al equipo"""
        try:
            if not self.email_user or not self.email_password:
                print("❌ Error: Credenciales de email no configuradas")
                print(f"EMAIL_REMITENTE: {self.email_user}")
                print(f"APP_PASSWORD_GMAIL: {'*' * len(self.email_password) if self.email_password else 'None'}")
                return False
            
            # Conectar al servidor SMTP (usando el mismo método que funciona en envio_correo.py)
            servidor = smtplib.SMTP_SSL("smtp.gmail.com")
            servidor.login(self.email_user, self.email_password)
            
            # 1. Correo de confirmación al lead
            msg_lead = EmailMessage()
            msg_lead['From'] = self.email_user
            msg_lead['To'] = correo
            msg_lead['Subject'] = f"✅ Reunión Corporativa Confirmada - {empresa} | DataPath"
            msg_lead.set_content(self.generar_mensaje_confirmacion_lead(nombre_contacto, empresa, fecha_reunion, hora_reunion))
            
            servidor.sendmail(self.email_user, correo, msg_lead.as_string())
            print(f"✅ Correo de confirmación enviado a: {correo}")
            
            # 2. Correo interno al equipo corporativo
            msg_interno = EmailMessage()
            msg_interno['From'] = self.email_user
            msg_interno['To'] = self.corporate_email
            msg_interno['Subject'] = f"🚨 NUEVA REUNIÓN B2B: {empresa} ({tamano_equipo} personas)"
            msg_interno.set_content(self.generar_mensaje_interno_equipo(nombre_contacto, empresa, correo, tamano_equipo, area_capacitacion, fecha_reunion, hora_reunion))
            
            servidor.sendmail(self.email_user, self.corporate_email, msg_interno.as_string())
            print(f"✅ Notificación interna enviada a: {self.corporate_email}")
            
            servidor.quit()
            return True
            
        except Exception as e:
            print(f"❌ Error enviando correos: {e}")
            return False
    
    def agendar_reunion_corporativa(self, nombre_contacto, empresa, correo, tamano_equipo, area_capacitacion, fecha_reunion, hora_reunion):
        """Función principal para agendar reunión corporativa"""
        try:
            print(f"🏢 Iniciando agendamiento corporativo para: {empresa}")
            
            # Obtener fecha/hora actual para logs
            info_actual = self.obtener_fecha_hora_actual()
            if info_actual:
                print(f"📅 Fecha actual: {info_actual['fecha_actual']}, {info_actual['hora_actual']}")
            
            # Validar fecha de reunión
            es_valida, mensaje = self.validar_fecha_reunion(fecha_reunion, hora_reunion)
            if not es_valida:
                return f"❌ Error: {mensaje}"
            
            # Crear evento en Google Calendar
            evento_creado, link_calendario = self.crear_evento_google_calendar(nombre_contacto, empresa, correo, fecha_reunion, hora_reunion)
            
            # Enviar correos
            if self.enviar_correos(nombre_contacto, empresa, correo, tamano_equipo, area_capacitacion, fecha_reunion, hora_reunion):
                # Incluir información del calendario si se creó correctamente
                info_calendario = ""
                if evento_creado and link_calendario:
                    info_calendario = f"\n📅 **Evento agregado a Google Calendar**: {link_calendario}"
                
                resultado = f"""
✅ **Reunión corporativa agendada exitosamente**

🏢 **{empresa}** - {tamano_equipo} personas
📅 **{fecha_reunion}** a las **{hora_reunion}**
👤 **Contacto:** {nombre_contacto}

Se han enviado las confirmaciones:
• Correo de confirmación a {nombre_contacto}
• Notificación interna al equipo comercial{info_calendario}

Nuestro equipo se pondrá en contacto en las próximas 2 horas para confirmar los detalles finales y enviar el enlace de la reunión.

¡Gracias por elegir DataPath para la capacitación de tu equipo! 🚀
"""
                print(f"✅ Reunión agendada: {empresa}")
                return resultado
            else:
                return "❌ Error enviando confirmaciones. Por favor, contacta directamente a nuestro equipo."
                
        except Exception as e:
            print(f"❌ Error agendando reunión: {e}")
            return f"❌ Error procesando tu solicitud: {str(e)}"

# Función de prueba (comentada)
# if __name__ == '__main__':
#     agenda = AgendaReunionCorporativa()
#     resultado = agenda.agendar_reunion_corporativa(
#         nombre_contacto="Juan Pérez",
#         empresa="TechCorp SAC",
#         correo="juan.perez@techcorp.com",
#         tamano_equipo="15",
#         area_capacitacion="Data Analytics",
#         fecha_reunion="Lunes 16 de Diciembre",
#         hora_reunion="10:00 AM"
#     )
#     print(resultado)
