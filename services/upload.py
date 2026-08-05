import os
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UploadService:
    
    UPLOAD_DIR = 'uploads'
    MAX_SIZE = 10 * 1024 * 1024
    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    
    @classmethod
    def init(cls):
        os.makedirs(f'{cls.UPLOAD_DIR}/produtos', exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/banners', exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/logos', exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/galeria', exist_ok=True)
        os.makedirs(f'{cls.UPLOAD_DIR}/temp', exist_ok=True)
    
    @classmethod
    def salvar_base64(cls, arquivo_base64: str, pasta: str = 'produtos') -> dict:
        try:
            if ',' in arquivo_base64:
                header, arquivo_base64 = arquivo_base64.split(',', 1)
            
            dados = base64.b64decode(arquivo_base64)
            
            if len(dados) > cls.MAX_SIZE:
                return {'sucesso': False, 'mensagem': 'Arquivo muito grande (máx 10MB)'}
            
            img = Image.open(BytesIO(dados))
            
            nome = f"{pasta}_{int(datetime.now().timestamp())}.png"
            caminho = f'{cls.UPLOAD_DIR}/{pasta}/{nome}'
            
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            
            img = img.convert('RGB') if img.mode in ('RGBA', 'P') else img
            img.save(caminho, 'PNG', optimize=True)
            
            logger.info(f'Upload salvo: {caminho}')
            return {'sucesso': True, 'caminho': caminho, 'nome': nome}
        except Exception as e:
            logger.error(f'Erro upload: {e}')
            return {'sucesso': False, 'mensagem': str(e)}
    
    @classmethod
    def redimensionar(cls, caminho: str, largura: int = 800, altura: int = 800) -> dict:
        try:
            img = Image.open(caminho)
            img.thumbnail((largura, altura), Image.LANCZOS)
            img.save(caminho, optimize=True)
            return {'sucesso': True, 'caminho': caminho}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @classmethod
    def deletar(cls, caminho: str) -> bool:
        try:
            if os.path.exists(caminho):
                os.remove(caminho)
                return True
            return False
        except:
            return False
