import os
import shutil
from datetime import datetime
from database.connection import get_db
import logging

logger = logging.getLogger(__name__)

class BackupService:
    
    BACKUP_DIR = 'backups'
    MAX_BACKUPS = 10
    
    @classmethod
    def init(cls):
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
    
    @classmethod
    def realizar_backup(cls) -> dict:
        try:
            cls.init()
            
            db = get_db()
            db.execute('VACUUM')
            
            nome = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            destino = os.path.join(cls.BACKUP_DIR, nome)
            
            db_path = db.execute('PRAGMA database_list').fetchone()[2]
            shutil.copy2(db_path, destino)
            
            # Remove backups antigos
            cls.limpar_backups_antigos()
            
            logger.info(f'💾 Backup criado: {nome}')
            return {'sucesso': True, 'arquivo': nome, 'caminho': destino}
        except Exception as e:
            logger.error(f'Erro backup: {e}')
            return {'sucesso': False, 'mensagem': str(e)}
    
    @classmethod
    def limpar_backups_antigos(cls):
        try:
            cls.init()
            arquivos = sorted(os.listdir(cls.BACKUP_DIR), reverse=True)
            for arquivo in arquivos[cls.MAX_BACKUPS:]:
                os.remove(os.path.join(cls.BACKUP_DIR, arquivo))
        except:
            pass
    
    @classmethod
    def listar_backups(cls) -> list:
        cls.init()
        backups = []
        for arquivo in sorted(os.listdir(cls.BACKUP_DIR), reverse=True):
            caminho = os.path.join(cls.BACKUP_DIR, arquivo)
            backups.append({
                'nome': arquivo,
                'tamanho': os.path.getsize(caminho),
                'data': datetime.fromtimestamp(os.path.getmtime(caminho)).isoformat()
            })
        return backups
    
    @classmethod
    def restaurar(cls, nome_arquivo: str) -> dict:
        try:
            db = get_db()
            db.close()
            
            caminho = os.path.join(cls.BACKUP_DIR, nome_arquivo)
            if not os.path.exists(caminho):
                return {'sucesso': False, 'mensagem': 'Arquivo não encontrado'}
            
            from config.geral import Config
            shutil.copy2(caminho, Config.DATABASE_PATH)
            
            return {'sucesso': True, 'mensagem': 'Backup restaurado! Reinicie o sistema.'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @classmethod
    def agendar_backup_automatico(cls):
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(cls.realizar_backup, 'cron', hour=3, minute=0)
        scheduler.start()
        logger.info('✅ Backup automático agendado (3:00 AM)')
