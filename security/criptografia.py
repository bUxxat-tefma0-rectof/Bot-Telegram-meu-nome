import base64
import hashlib
from cryptography.fernet import Fernet
from config.seguranca import SegurancaConfig
import logging

logger = logging.getLogger(__name__)

class CryptoService:
    
    _fernet = None
    
    @classmethod
    def _get_fernet(cls):
        if cls._fernet is None:
            key = hashlib.sha256(SegurancaConfig.JWT_SECRET.encode()).digest()
            cls._fernet = Fernet(base64.urlsafe_b64encode(key[:32]))
        return cls._fernet
    
    @classmethod
    def criptografar(cls, texto: str) -> str:
        try:
            fernet = cls._get_fernet()
            return fernet.encrypt(texto.encode()).decode()
        except Exception as e:
            logger.error(f'Erro ao criptografar: {e}')
            return texto
    
    @classmethod
    def descriptografar(cls, texto_criptografado: str) -> str:
        try:
            fernet = cls._get_fernet()
            return fernet.decrypt(texto_criptografado.encode()).decode()
        except Exception as e:
            logger.error(f'Erro ao descriptografar: {e}')
            return texto_criptografado
    
    @classmethod
    def hash_sha256(cls, texto: str) -> str:
        return hashlib.sha256(texto.encode()).hexdigest()
    
    @classmethod
    def hash_md5(cls, texto: str) -> str:
        return hashlib.md5(texto.encode()).hexdigest()
    
    @classmethod
    def gerar_token_unico(cls) -> str:
        import uuid
        return str(uuid.uuid4())
    
    @classmethod
    def mascarar_dados(cls, texto: str, tipo: str = 'email') -> str:
        if tipo == 'email':
            partes = texto.split('@')
            if len(partes) == 2:
                return f'{partes[0][:2]}***@{partes[1]}'
        elif tipo == 'telefone':
            return f'{texto[:4]}****{texto[-2:]}' if len(texto) > 6 else '****'
        elif tipo == 'cpf':
            return f'***.{texto[3:6]}.***-**' if len(texto) >= 11 else '***'
        return '***'
