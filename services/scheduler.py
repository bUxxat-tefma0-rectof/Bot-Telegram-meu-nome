from apscheduler.schedulers.background import BackgroundScheduler
from services.backup import BackupService
from services.notificacoes import NotificacaoService
from services.estoque import EstoqueService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def iniciar(self):
        # Backup diário (3h da manhã)
        self.scheduler.add_job(
            BackupService.realizar_backup,
            'cron',
            hour=3,
            minute=0,
            id='backup_diario'
        )
        
        # Verificar estoque baixo (a cada 30 min)
        self.scheduler.add_job(
            EstoqueService.verificar_estoque_baixo,
            'interval',
            minutes=30,
            id='estoque_baixo'
        )
        
        # Notificar aniversariantes (9h da manhã)
        self.scheduler.add_job(
            NotificacaoService.notificar_aniversariantes,
            'cron',
            hour=9,
            minute=0,
            id='aniversariantes'
        )
        
        # Limpar carrinhos abandonados (a cada 6 horas)
        self.scheduler.add_job(
            self.limpar_carrinhos_abandonados,
            'interval',
            hours=6,
            id='carrinhos_abandonados'
        )
        
        # Limpar logs antigos (domingo meia-noite)
        self.scheduler.add_job(
            self.limpar_logs_antigos,
            'cron',
            day_of_week='sun',
            hour=0,
            minute=0,
            id='limpar_logs'
        )
        
        self.scheduler.start()
        logger.info('✅ Agendador iniciado')
    
    def limpar_carrinhos_abandonados(self):
        from database.connection import get_db
        db = get_db()
        db.execute("DELETE FROM carrinhos WHERE data_adicao < datetime('now', '-24 hours')")
        db.commit()
        logger.info('🗑 Carrinhos abandonados limpos')
    
    def limpar_logs_antigos(self):
        from database.connection import get_db
        db = get_db()
        db.execute("DELETE FROM logs_sistema WHERE data < datetime('now', '-90 days')")
        db.commit()
        logger.info('🗑 Logs antigos limpos')
    
    def parar(self):
        self.scheduler.shutdown()
