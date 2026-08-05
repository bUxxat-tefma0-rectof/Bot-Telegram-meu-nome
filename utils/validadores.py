import re
from typing import Dict, Any

class Validador:
    
    @staticmethod
    def validar_nome(nome: str) -> Dict[str, Any]:
        """Valida nome completo"""
        if not nome or len(nome.strip()) < 3:
            return {'valido': False, 'erro': 'Nome deve ter pelo menos 3 caracteres'}
        if len(nome.strip().split()) < 2:
            return {'valido': False, 'erro': 'Digite nome e sobrenome'}
        return {'valido': True, 'nome': nome.strip()}
    
    @staticmethod
    def validar_email(email: str) -> Dict[str, Any]:
        """Valida email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(pattern, email):
            return {'valido': False, 'erro': 'Email inválido'}
        return {'valido': True, 'email': email.lower().strip()}
    
    @staticmethod
    def validar_telefone(telefone: str) -> Dict[str, Any]:
        """Valida telefone brasileiro"""
        tel = re.sub(r'[^0-9]', '', str(telefone))
        if len(tel) not in [10, 11]:
            return {'valido': False, 'erro': 'Telefone deve ter 10 ou 11 dígitos'}
        return {'valido': True, 'telefone': tel}
    
    @staticmethod
    def validar_senha(senha: str) -> Dict[str, Any]:
        """Valida senha"""
        if not senha or len(senha) < 6:
            return {'valido': False, 'erro': 'Senha deve ter no mínimo 6 caracteres'}
        return {'valido': True}
    
    @staticmethod
    def validar_cep(cep: str) -> Dict[str, Any]:
        """Valida CEP"""
        cep_limpo = re.sub(r'[^0-9]', '', str(cep))
        if len(cep_limpo) != 8:
            return {'valido': False, 'erro': 'CEP deve ter 8 dígitos'}
        return {'valido': True, 'cep': cep_limpo}
    
    @staticmethod
    def validar_valor(valor: Any, minimo: float = 0) -> Dict[str, Any]:
        """Valida valor monetário"""
        try:
            v = float(valor)
            if v < minimo:
                return {'valido': False, 'erro': f'Valor mínimo: R$ {minimo:.2f}'}
            return {'valido': True, 'valor': v}
        except:
            return {'valido': False, 'erro': 'Valor inválido'}
    
    @staticmethod
    def validar_quantidade(qtd: Any, maximo: int = 999) -> Dict[str, Any]:
        """Valida quantidade"""
        try:
            q = int(qtd)
            if q < 1:
                return {'valido': False, 'erro': 'Quantidade mínima: 1'}
            if q > maximo:
                return {'valido': False, 'erro': f'Quantidade máxima: {maximo}'}
            return {'valido': True, 'quantidade': q}
        except:
            return {'valido': False, 'erro': 'Quantidade inválida'}
