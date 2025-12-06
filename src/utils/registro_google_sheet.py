import pygsheets #pip install pygsheets
import pandas as pd #pip install pandas
import os
from dotenv import load_dotenv

load_dotenv()

class RegistroGoogleSheet:
    ## conexion a google sheets
    def registrar_google_sheets(self, nombre, correo, celular, programa):
        try:
            # Obtener configuraciones desde variables de entorno
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Interesados")  # Default: "Interesados"
            service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
            
            # Validaciones
            if not sheet_id:
                print("❌ Error: GOOGLE_SHEET_ID no configurado en .env")
                return False
                
            if not service_account_path:
                print("❌ Error: GOOGLE_SERVICE_ACCOUNT_PATH no configurado en .env")
                return False
                
            if not os.path.exists(service_account_path):
                print(f"❌ Error: Archivo de credenciales no encontrado: {service_account_path}")
                return False
            
            print(f"📊 Registrando en Google Sheet - ID: {sheet_id[:10]}..., Hoja: {sheet_name}")
            
            # URL para leer datos actuales
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            
            # Leer datos actuales del sheet
            try:
                df = pd.read_csv(url)
                print(f"📋 Datos actuales leídos: {len(df)} registros")
            except Exception as e:
                print(f"⚠️ Error leyendo sheet, creando nuevo: {e}")
                # Si no se puede leer, crear un DataFrame vacío con las columnas esperadas
                df = pd.DataFrame(columns=['ID', 'Nombre', 'Correo', 'Celular', 'Programa'])
            
            # Generar ID único (timestamp o contador)
            import time
            new_id = int(time.time())  # Usar timestamp como ID
            
            # Añadir nuevo registro
            new_row = {'ID': new_id, 'Nombre': nombre, 'Correo': correo, 'Celular': celular, 'Programa': programa}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            print(f"➕ Agregando registro: {nombre} - {correo} - {celular} - {programa}")
            
            # Conectar a Google Sheets
            gc = pygsheets.authorize(service_file=service_account_path)
            
            # Abrir spreadsheet por ID (más confiable que por URL)
            sh = gc.open_by_key(sheet_id)
            
            # Seleccionar la hoja por nombre
            try:
                wks = sh.worksheet_by_title(sheet_name)
            except:
                # Si la hoja no existe, usar la primera
                wks = sh[0]
                print(f"⚠️ Hoja '{sheet_name}' no encontrada, usando la primera hoja")
            
            # Actualizar la hoja con el DataFrame completo
            wks.set_dataframe(df, (1, 1))  # Empezar en A1
            
            print(f"✅ Registro exitoso en Google Sheet: {nombre}")
            return True
            
        except Exception as e:
            print(f"❌ Error registrando en Google Sheet: {str(e)}")
            return False

if __name__ == '__main__':
    registrador = RegistroGoogleSheet()
    registrador.registrar_google_sheets(nombre="Jeanpier Ancori", correo="tarara.tarara@gmail.com", celular="+51987654321", programa="Data Engineer Program")

#python3 utils/registro_google_sheet.py