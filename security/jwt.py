import jwt
from datetime import datetime, timedelta
from config.seguranca import SegurancaConfig
from typing import Optional, Dict

class JWTHandler:
    
    SECRET = SegurancaConfig.JWT_SECRET
    ALGORITHM = 'HS256'
    EXPIRACAO = SegurancaConfig.JWT_EXPIRACAO_HORAS
    
    @classmethod
    def gerar_token(cls, user_id: int, dados_extra: Dict = None) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=cls.EXPIRACAO),
            'iat': datetime.utcnow()
        }
        if dados_extra:
            payload.update(dados_extra)
        
        return jwt.encode(payload, cls.SECRET, algorithm=cls.ALGORITHM)
    
    @classmethod
    def verificar_token(cls, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, cls.SECRET, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @classmethod
    def get_user_id(cls, token: str) -> Optional[int]:
        payload = cls.verificar_token(token)
        return payload.get('user_id') if payload else None
    
    @classmethod
    def refresh_token(cls, token: str) -> Optional[str]:
        payload = cls.verificar_token(token)
        if payload:
            return cls.gerar_token(payload['user_id'])
        return None
