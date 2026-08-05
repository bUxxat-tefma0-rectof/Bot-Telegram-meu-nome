import hashlib
import hmac
from database.connection import get_db
from config.seguranca import SegurancaConfig
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SecurityAuth:
    
    @staticmethod
    def hash_senha(senha: str) -> str:
        salt = SegurancaConfig.JWT_SECRET[:16]
        return hashlib.pbkdf2_hmac('sha256', senha.encode(), salt.encode(), 100000).hex()
    
    @staticmethod
    def verificar_senha(senha: str, hash_armazenado: str) -> bool:
        return SecurityAuth.hash_senha(senha) == hash_armazenado
    
    @staticmethod
    def verificar_2fa(user_id: int, codigo: str) -> bool:
        if not SegurancaConfig.DOIS_FATORES_ATIVO:
            return True
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE id = ?', (user_id,)).fetchone()
        if not cliente or not cliente.get('token_2fa'):
            return True
        return codigo == cliente['token_2fa']
    
    @staticmethod
    def get_tentativas_restantes(user_id: int) -> int:
        from security.rate_limit import RateLimiter
        return RateLimiter.get_tentativas_restantes(user_id)
    
    @staticmethod
    def registrar_tentativa(user_id: int, sucesso: bool):
        db = get_db()
        db.execute('''
            INSERT INTO logs_sistema (usuario_id, acao, modulo, detalhes, data)
            VALUES (?, ?, 'auth', ?, datetime('now'))
        ''', (user_id, 'login_sucesso' if sucesso else 'login_falha', 
              'Login realizado' if sucesso else 'Tentativa de login falhou'))
        db.commit()
