from services.backup import BackupService
from database.connection import get_db

class BackupAdmin:
    
    @staticmethod
    def criar() -> dict:
        return BackupService.realizar_backup()
    
    @staticmethod
    def listar() -> list:
        return BackupService.listar_backups()
    
    @staticmethod
    def restaurar(nome_arquivo: str) -> dict:
        return BackupService.restaurar(nome_arquivo)
    
    @staticmethod
    def agendar() -> dict:
        BackupService.agendar_backup_automatico()
        return {'sucesso': True, 'mensagem': 'Backup automático agendado para 3:00 AM'}
    
    @staticmethod
    def get_config() -> dict:
        db = get_db()
        return {
            'backup_automatico': db.execute("SELECT valor FROM configuracoes WHERE chave='backup_automatico'").fetchone()['valor'] == '1' if db.execute("SELECT valor FROM configuracoes WHERE chave='backup_automatico'").fetchone() else False,
            'max_backups': int(db.execute("SELECT valor FROM configuracoes WHERE chave='max_backups'").fetchone()['valor']) if db.execute("SELECT valor FROM configuracoes WHERE chave='max_backups'").fetchone() else 10
        }
