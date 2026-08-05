import os
import base64
from io import BytesIO
from PIL import Image
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ImagemUtil:
    
    UPLOAD_DIR = 'uploads'
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    
    @classmethod
    def init_dirs(cls):
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/produtos', exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/banners', exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/logos', exist_ok=True)
    
    @classmethod
    def salvar_imagem(cls, arquivo_base64: str, pasta: str = 'produtos') -> Optional[str]:
        try:
            if ',' in arquivo_base64:
                arquivo_base64 = arquivo_base64.split(',')[1]
            
            dados = base64.b64decode(arquivo_base64)
            
            if len(dados) > cls.MAX_SIZE:
                return None
            
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(dados))
            
            nome_arquivo = f"{pasta}_{int(datetime.now().timestamp())}.png"
            caminho = f'{cls.UPLOAD_DIR}/{pasta}/{nome_arquivo}'
            
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            img.save(caminho, 'PNG', optimize=True)
            
            return caminho
        except Exception as e:
            logger.error(f'Erro ao salvar imagem: {e}')
            return None
    
    @classmethod
    def redimensionar(cls, caminho: str, largura: int = 800, altura: int = 800) -> Optional[str]:
        try:
            img = Image.open(caminho)
            img.thumbnail((largura, altura), Image.LANCZOS)
            img.save(caminho, optimize=True)
            return caminho
        except Exception as e:
            logger.error(f'Erro ao redimensionar: {e}')
            return None
    
    @classmethod
    def download_imagem(cls, url: str, pasta: str = 'produtos') -> Optional[str]:
        try:
            resp = requests.get(url, timeout=10, stream=True)
            if resp.status_code == 200:
                nome = f"{pasta}_{int(datetime.now().timestamp())}.jpg"
                caminho = f'{cls.UPLOAD_DIR}/{pasta}/{nome}'
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                with open(caminho, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                return caminho
        except:
            pass
        return None

from datetime import datetime
