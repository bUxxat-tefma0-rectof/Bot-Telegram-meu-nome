import re
from datetime import datetime

class Formatador:
    
    @staticmethod
    def moeda(valor: float) -> str:
        if valor is None: return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def data(data, formato: str = "%d/%m/%Y %H:%M") -> str:
        if data is None: return ""
        if isinstance(data, str):
            try: data = datetime.fromisoformat(data.replace('Z', '+00:00'))
            except: return data
        return data.strftime(formato)
    
    @staticmethod
    def data_curta(data) -> str:
        return Formatador.data(data, "%d/%m/%Y")
    
    @staticmethod
    def hora(data) -> str:
        return Formatador.data(data, "%H:%M")
    
    @staticmethod
    def cpf(cpf: str) -> str:
        cpf = re.sub(r'[^0-9]', '', str(cpf))
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf
    
    @staticmethod
    def telefone(tel: str) -> str:
        tel = re.sub(r'[^0-9]', '', str(tel))
        if len(tel) == 11: return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        return tel
    
    @staticmethod
    def cep(cep: str) -> str:
        cep = re.sub(r'[^0-9]', '', str(cep))
        return f"{cep[:5]}-{cep[3:]}" if len(cep) == 8 else cep
    
    @staticmethod
    def porcentagem(valor: float) -> str:
        return f"{valor:.1f}%"
    
    @staticmethod
    def numero(valor: int) -> str:
        return f"{valor:,}".replace(",", ".")
    
    @staticmethod
    def status_pedido(status: str) -> str:
        status_map = {
            'recebido': '📥 Recebido',
            'confirmado': '✅ Confirmado',
            'separando': '📦 Separando',
            'entregue': '🏠 Entregue',
            'cancelado': '❌ Cancelado'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def status_pagamento(status: str) -> str:
        status_map = {
            'pendente': '⏳ Pendente',
            'approved': '✅ Aprovado',
            'rejected': '❌ Recusado',
            'refunded': '💰 Reembolsado'
        }
        return status_map.get(status, status)
