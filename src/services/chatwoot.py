"""
Servicio para interactuar con Chatwoot
Documentación: https://www.chatwoot.com/developers/api/
"""
import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class Chatwoot:
    """Cliente para Chatwoot - Gestión de conversaciones y tickets"""

    def __init__(self):
        # Configuración desde variables de entorno
        self.base_url = os.getenv('CHATWOOT_BASE_URL', 'http://chatwoot:3000').rstrip('/')
        self.api_key = os.getenv('CHATWOOT_API_ACCESS_TOKEN')
        self.account_id = os.getenv('CHATWOOT_ACCOUNT_ID', '1')
        
        # Headers por defecto
        self.headers = {
            'Content-Type': 'application/json',
            'api_access_token': self.api_key
        }

    def create_conversation(
        self, 
        contact_id: int,
        inbox_id: int,
        message: str,
        assignee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva conversación en Chatwoot
        
        Args:
            contact_id: ID del contacto en Chatwoot
            inbox_id: ID del inbox (canal)
            message: Primer mensaje de la conversación
            assignee_id: ID del agente asignado (opcional)
            
        Returns:
            Datos de la conversación creada
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations'
        
        payload = {
            'contact_id': contact_id,
            'inbox_id': inbox_id,
            'message': message
        }
        
        if assignee_id:
            payload['assignee_id'] = assignee_id
        
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al crear conversación: {e}")
            return {'error': str(e)}

    def send_message(
        self,
        conversation_id: int,
        message: str,
        message_type: str = 'outgoing',
        private: bool = False
    ) -> Dict[str, Any]:
        """
        Envía un mensaje en una conversación existente
        
        Args:
            conversation_id: ID de la conversación
            message: Texto del mensaje
            message_type: 'outgoing' (bot/agente) o 'incoming' (usuario)
            private: Si es nota privada (solo visible para agentes)
            
        Returns:
            Datos del mensaje enviado
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages'
        
        payload = {
            'content': message,
            'message_type': message_type,
            'private': private
        }
        
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar mensaje a Chatwoot: {e}")
            return {'error': str(e)}

    def get_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """
        Obtiene los detalles de una conversación
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Datos de la conversación
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}'
        
        try:
            response = requests.get(
                url=url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener conversación: {e}")
            return {'error': str(e)}

    def get_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los mensajes de una conversación
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Lista de mensajes
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages'
        
        try:
            response = requests.get(
                url=url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('payload', [])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener mensajes: {e}")
            return []

    def create_contact(
        self,
        name: str,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        custom_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo contacto en Chatwoot
        
        Args:
            name: Nombre del contacto
            phone_number: Número de teléfono
            email: Correo electrónico
            custom_attributes: Atributos personalizados
            
        Returns:
            Datos del contacto creado
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/contacts'
        
        payload = {
            'name': name
        }
        
        if phone_number:
            payload['phone_number'] = phone_number
        if email:
            payload['email'] = email
        if custom_attributes:
            payload['custom_attributes'] = custom_attributes
        
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al crear contacto: {e}")
            return {'error': str(e)}

    def update_contact(
        self,
        contact_id: int,
        custom_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza los atributos personalizados de un contacto
        
        Args:
            contact_id: ID del contacto
            custom_attributes: Diccionario con atributos a actualizar
            
        Returns:
            Datos del contacto actualizado
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/contacts/{contact_id}'
        
        payload = {
            'custom_attributes': custom_attributes
        }
        
        try:
            response = requests.patch(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al actualizar contacto: {e}")
            return {'error': str(e)}

    def toggle_status(
        self,
        conversation_id: int,
        status: str = 'resolved'
    ) -> Dict[str, Any]:
        """
        Cambia el estado de una conversación
        
        Args:
            conversation_id: ID de la conversación
            status: 'open', 'pending', 'resolved', 'snoozed'
            
        Returns:
            Datos de la conversación actualizada
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/toggle_status'
        
        payload = {
            'status': status
        }
        
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al cambiar estado: {e}")
            return {'error': str(e)}

    def assign_conversation(
        self,
        conversation_id: int,
        assignee_id: Optional[int] = None,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Asigna una conversación a un agente o equipo
        
        Args:
            conversation_id: ID de la conversación
            assignee_id: ID del agente
            team_id: ID del equipo
            
        Returns:
            Datos de la conversación actualizada
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/assignments'
        
        payload = {}
        if assignee_id:
            payload['assignee_id'] = assignee_id
        if team_id:
            payload['team_id'] = team_id
        
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al asignar conversación: {e}")
            return {'error': str(e)}

    def add_labels(
        self,
        conversation_id: int,
        labels: List[str]
    ) -> Dict[str, Any]:
        """
        Agrega etiquetas a una conversación
        
        Args:
            conversation_id: ID de la conversación
            labels: Lista de etiquetas a agregar
            
        Returns:
            Resultado de la operación
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/labels'
        
        payload = {
            'labels': labels
        }
        
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al agregar etiquetas: {e}")
            return {'error': str(e)}
    
    def remove_labels(
        self,
        conversation_id: int,
        labels: List[str]
    ) -> Dict[str, Any]:
        """
        Elimina etiquetas de una conversación
        
        Args:
            conversation_id: ID de la conversación
            labels: Lista de etiquetas a eliminar
            
        Returns:
            Resultado de la operación
        """
        url = f'{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/labels'
        
        payload = {
            'labels': labels
        }
        
        try:
            response = requests.delete(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al eliminar etiquetas: {e}")
            return {'error': str(e)}
    
    def get_conversation_labels(
        self,
        conversation_id: int
    ) -> List[str]:
        """
        Obtiene las etiquetas de una conversación
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Lista de nombres de etiquetas
        """
        # Obtenemos los detalles de la conversación
        conversation_data = self.get_conversation(conversation_id)
        
        if 'error' in conversation_data:
            print(f"Error al obtener etiquetas: {conversation_data['error']}")
            return []
        
        # Extraer etiquetas del objeto conversación
        labels = conversation_data.get('labels', [])
        
        # Las etiquetas pueden venir como strings o como objetos
        if labels and isinstance(labels[0], str):
            return labels
        elif labels and isinstance(labels[0], dict):
            return [label.get('title', '') for label in labels]
        
        return []

