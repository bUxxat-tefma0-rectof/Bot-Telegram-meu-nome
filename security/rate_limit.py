from collections import defaultdict
from datetime import datetime, timedelta
from config.seguranca import SegurancaConfig
import threading

class RateLimiter:
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._requests = defaultdict(list)
            cls._instance._bloqueios = {}
        return cls._instance
    
    def verificar(self, user_id: int, limite: int = None, janela: int = 60) -> bool:
        if limite is None:
            limite = SegurancaConfig.MAX_REQUISICOES_POR_MINUTO
        
        agora = datetime.now()
        janela_tempo = timedelta(seconds=janela)
        
        with self._lock:
            # Limpa requisições antigas
            self._requests[user_id] = [r for r in self._requests[user_id] if agora - r < janela_tempo]
            
            # Verifica bloqueio
            if user_id in self._bloqueios:
                if agora < self._bloqueios[user_id]:
                    return False
                del self._bloqueios[user_id]
            
            # Verifica limite
            if len(self._requests[user_id]) >= limite:
                self._bloqueios[user_id] = agora + timedelta(minutes=SegurancaConfig.BLOQUEIO_TEMPORARIO_MINUTOS)
                return False
            
            self._requests[user_id].append(agora)
            return True
    
    @classmethod
    def get_tentativas_restantes(cls, user_id: int) -> int:
        instance = cls()
        agora = datetime.now()
        janela = timedelta(seconds=60)
        instance._requests[user_id] = [r for r in instance._requests.get(user_id, []) if agora - r < janela]
        limite = SegurancaConfig.MAX_REQUISICOES_POR_MINUTO
        return max(0, limite - len(instance._requests.get(user_id, [])))
    
    def reset(self, user_id: int):
        with self._lock:
            self._requests[user_id] = []
            if user_id in self._bloqueios:
                del self._bloqueios[user_id]
