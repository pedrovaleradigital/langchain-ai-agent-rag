# LangChain v1.0: Los tools ahora se importan desde langchain_core
from langchain_core.tools import tool, StructuredTool

from utils.envio_correo import EnvioCorreo
from utils.registro_google_sheet import RegistroGoogleSheet
from utils.agenda_reunion_corporativa import AgendaReunionCorporativa

from bot.ai_bot import AIBot

import os

class PedroTools:

    @staticmethod
    def enviar_correo_func(nombre_lead: str, correo_lead: str, mensaje_para_lead: str):
        """Envía un correo necesitando solo el nombre del interesado, el correo del interesado y un mensaje para el interesado que va a depender del programa en el cuál él tenga el interés."""
        envio = EnvioCorreo()
        envio.enviar_correo(nombre_lead, correo_lead, mensaje_para_lead)
    
    enviar_correo = StructuredTool.from_function(
        enviar_correo_func,
        name="enviar_correo",
        description="Envía un correo necesitando solo el nombre del interesado, el correo del interesado y un mensaje para el interesado que va a depender del programa en el cuál él tenga el interés."
    )

    @staticmethod
    def registrar_google_sheet_func(nombre: str, correo: str, celular: str, programa: str):
        """Registra los datos del interesado pidiendo nombre completo, correo electrónico, número de celular y programa de interés."""
        registro = RegistroGoogleSheet()
        registro.registrar_google_sheets(nombre, correo, celular, programa)
    
    # Crear la herramienta estructurada
    registrar_google_sheet = StructuredTool.from_function(
        registrar_google_sheet_func,
        name="registrar_google_sheet",
        description="Registra los datos del interesado pidiendo nombre completo, correo electrónico, número de celular y programa de interés en Google Sheets. Usa esta herramienta DESPUÉS de recopilar toda la información del lead interesado en inscribirse."
    )
    
    @staticmethod
    def consultar_RAG_func(query: str, history_messages=None) -> str:
        """Usa el sistema RAG para buscar información sobre DataPath y devuelve la respuesta."""
        # Imprime lo que recibe la tool en el parámetro history_messages
        print("En la tool 'consultar_RAG', history_messages recibido:")
        print(history_messages)
        
        rag_instance = AIBot()  # Inicializar el sistema RAG
        
        try:
            # 1. Buscar documentos relevantes (devuelve lista de objetos Document)
            docs = rag_instance.search_similar_documents(query)
            
            if not docs:
                return "No se encontró información relevante en la base de conocimientos."
                
            # 2. Formatear los documentos como texto plano para el agente
            formatted_context = "\n\n".join([f"--- Documento {i+1} ---\n{doc.page_content}" for i, doc in enumerate(docs)])
            
            return f"Información recuperada de la base de conocimientos:\n\n{formatted_context}"
            
        except Exception as e:
            print(f"Error al consultar RAG: {e}")
            return f"Error al consultar la base de conocimientos: {str(e)}"

    # Crear la herramienta estructurada con el nuevo nombre
    consultar_RAG = StructuredTool.from_function(
        consultar_RAG_func,
        name="consultar_RAG",
        description="Usa el sistema RAG para consultar la base de conocimiento de Pedro. Devuelve fragmentos de texto relevantes."
    )
    
    # ============================================================================
    # NUEVA TOOL: AGENDA REUNIÓN CORPORATIVA
    # ============================================================================
    
    @staticmethod
    def agendar_reunion_corporativa_func(nombre_contacto: str, empresa: str, correo: str, tamano_equipo: str, area_capacitacion: str, fecha_reunion: str, hora_reunion: str):
        """Agenda reunión corporativa para capacitación empresarial cuando detecta intención B2B"""
        agenda = AgendaReunionCorporativa()
        return agenda.agendar_reunion_corporativa(nombre_contacto, empresa, correo, tamano_equipo, area_capacitacion, fecha_reunion, hora_reunion)
    
    # Crear la herramienta estructurada para reuniones corporativas
    agendar_reunion_corporativa = StructuredTool.from_function(
        agendar_reunion_corporativa_func,
        name="agendar_reunion_corporativa",
        description="Agenda reunión con el equipo comercial corporativo cuando detecta intención de capacitación empresarial. Se activa cuando el usuario menciona: 'mi empresa', 'mi equipo', 'capacitación corporativa', 'entrenar empleados', etc. Requiere: nombre del contacto, nombre de la empresa, correo corporativo, tamaño del equipo, área de capacitación, fecha preferida y hora preferida para la reunión."
    )

    