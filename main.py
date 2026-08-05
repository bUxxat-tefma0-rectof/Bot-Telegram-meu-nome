"""
Loja Digital Telegram - Sistema Completo
Totalmente editável pelo painel administrativo
"""

import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.geral import Config
from database.connection import init_database
from services.scheduler import SchedulerService
from services.logs import LogService
from services.backup import BackupService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('logs/loja.log', encoding='utf-8')]
)
logger = logging.getLogger(__name__)

class LojaDigital:
    def __init__(self):
        self.config = Config()
        self.scheduler = SchedulerService()
        
    def iniciar(self):
        logger.info('🛒 Iniciando Loja Digital Telegram...')
        
        # Banco de dados
        init_database()
        logger.info('✅ Banco de dados pronto')
        
        # Backup automático
        BackupService.agendar_backup_automatico()
        
        # Bots
        from bot.cliente import start_bot_cliente
        from bot.admin import start_bot_admin
        
        threading.Thread(target=start_bot_cliente, daemon=True).start()
        logger.info('✅ Bot Cliente iniciado')
        
        threading.Thread(target=start_bot_admin, daemon=True).start()
        logger.info('✅ Bot Admin iniciado')
        
        # Agendador
        self.scheduler.iniciar()
        logger.info('✅ Agendador iniciado')
        
        # Servidor Web (WebApp)
        from webapp import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))
        
        logger.info('🛒 Loja Digital pronta!')

if __name__ == '__main__':
    loja = LojaDigital()
    loja.iniciar()
