import os
from typing import Optional, Dict, List
from telegram import Bot
from config.geral import Config
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    
    _bot_cliente = None
    _bot_admin = None
    
    @classmethod
    def get_bot_cliente(cls) -> Optional[Bot]:
        if cls._bot_cliente is None and Config.BOT_TOKEN_CLIENTE:
            cls._bot_cliente = Bot(token=Config.BOT_TOKEN_CLIENTE)
        return cls._bot_cliente
    
    @classmethod
    def get_bot_admin(cls) -> Optional[Bot]:
        if cls._bot_admin is None and Config.BOT_TOKEN_ADMIN:
            cls._bot_admin = Bot(token=Config.BOT_TOKEN_ADMIN)
        return cls._bot_admin
    
    @classmethod
    async def enviar_mensagem(cls, chat_id: int, texto: str, parse_mode: str = 'Markdown',
                              reply_markup=None) -> bool:
        try:
            bot = cls.get_bot_cliente()
            if bot:
                await bot.send_message(chat_id=chat_id, text=texto, 
                                       parse_mode=parse_mode, reply_markup=reply_markup)
                return True
        except Exception as e:
            logger.error(f'Erro ao enviar mensagem: {e}')
        return False
    
    @classmethod
    async def enviar_foto(cls, chat_id: int, foto: str, caption: str = None) -> bool:
        try:
            bot = cls.get_bot_cliente()
            if bot:
                await bot.send_photo(chat_id=chat_id, photo=foto, caption=caption, parse_mode='Markdown')
                return True
        except Exception as e:
            logger.error(f'Erro ao enviar foto: {e}')
        return False
    
    @classmethod
    async def enviar_para_todos(cls, texto: str, clientes: List[int]) -> Dict:
        bot = cls.get_bot_cliente()
        if not bot:
            return {'enviados': 0, 'falhas': len(clientes)}
        
        enviados = 0
        falhas = 0
        
        for chat_id in clientes:
            try:
                await bot.send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
                enviados += 1
            except:
                falhas += 1
        
        return {'enviados': enviados, 'falhas': falhas}
    
    @classmethod
    async def get_file_url(cls, file_id: str) -> Optional[str]:
        try:
            bot = cls.get_bot_cliente()
            if bot:
                file = await bot.get_file(file_id)
                return file.file_path
        except:
            pass
        return None
