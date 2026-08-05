import os
import json
from datetime import datetime
from typing import Optional, Dict, List

class StorageService:
    
    STORAGE_DIR = 'storage'
    
    @classmethod
    def init(cls):
        os.makedirs(cls.STORAGE_DIR, exist_ok=True)
        os.makedirs(f'{cls.STORAGE_DIR}/temp', exist_ok=True)
        os.makedirs(f'{cls.STORAGE_DIR}/exports', exist_ok=True)
        os.makedirs(f'{cls.STORAGE_DIR}/imports', exist_ok=True)
    
    @classmethod
    def salvar_arquivo(cls, nome: str, conteudo: bytes, pasta: str = '') -> str:
        cls.init()
        if pasta:
            os.makedirs(f'{cls.STORAGE_DIR}/{pasta}', exist_ok=True)
            caminho = f'{cls.STORAGE_DIR}/{pasta}/{nome}'
        else:
            caminho = f'{cls.STORAGE_DIR}/{nome}'
        
        with open(caminho, 'wb') as f:
            f.write(conteudo)
        
        return caminho
    
    @classmethod
    def ler_arquivo(cls, caminho: str) -> Optional[bytes]:
        if not os.path.exists(caminho):
            return None
        with open(caminho, 'rb') as f:
            return f.read()
    
    @classmethod
    def deletar_arquivo(cls, caminho: str) -> bool:
        if os.path.exists(caminho):
            os.remove(caminho)
            return True
        return False
    
    @classmethod
    def listar_arquivos(cls, pasta: str = '') -> List[Dict]:
        cls.init()
        dir_path = f'{cls.STORAGE_DIR}/{pasta}' if pasta else cls.STORAGE_DIR
        if not os.path.exists(dir_path):
            return []
        
        arquivos = []
        for nome in os.listdir(dir_path):
            caminho = os.path.join(dir_path, nome)
            if os.path.isfile(caminho):
                arquivos.append({
                    'nome': nome,
                    'tamanho': os.path.getsize(caminho),
                    'data': datetime.fromtimestamp(os.path.getmtime(caminho)).isoformat()
                })
        return sorted(arquivos, key=lambda x: x['data'], reverse=True)
    
    @classmethod
    def limpar_temp(cls):
        cls.init()
        temp_dir = f'{cls.STORAGE_DIR}/temp'
        if os.path.exists(temp_dir):
            for arquivo in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, arquivo))
