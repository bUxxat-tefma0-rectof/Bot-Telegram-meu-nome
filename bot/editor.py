from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database.connection import get_db

class EditorService:
    
    @staticmethod
    def editar_mensagem_simples(message, novo_texto: str, kb: list = None):
        """Edita uma mensagem existente"""
        try:
            if kb:
                return message.edit_text(novo_texto, parse_mode='Markdown', 
                                        reply_markup=InlineKeyboardMarkup(kb))
            return message.edit_text(novo_texto, parse_mode='Markdown')
        except:
            if kb:
                return message.reply_text(novo_texto, parse_mode='Markdown',
                                         reply_markup=InlineKeyboardMarkup(kb))
            return message.reply_text(novo_texto, parse_mode='Markdown')
    
    @staticmethod
    def editar_apenas_botoes(message, kb: list):
        """Edita apenas os botões de uma mensagem"""
        try:
            return message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(kb))
        except:
            pass
    
    @staticmethod
    def editar_apenas_texto(message, novo_texto: str):
        """Edita apenas o texto de uma mensagem"""
        try:
            return message.edit_text(novo_texto, parse_mode='Markdown')
        except:
            pass
    
    @staticmethod
    def get_botoes_menu(menu: str) -> list:
        """Busca botões do menu no banco de dados"""
        db = get_db()
        botoes = db.execute(
            "SELECT * FROM botoes_menu WHERE menu = ? AND ativo = 1 ORDER BY linha, ordem",
            (menu,)
        ).fetchall()
        
        kb = []
        linha_atual = 0
        row = []
        
        for btn in botoes:
            if btn['linha'] != linha_atual:
                if row:
                    kb.append(row)
                row = []
                linha_atual = btn['linha']
            
            texto = f"{btn['emoji'] or ''} {btn['texto']}"
            if btn['url']:
                row.append(InlineKeyboardButton(texto, url=btn['url']))
            else:
                row.append(InlineKeyboardButton(texto, callback_data=btn['callback_data']))
        
        if row:
            kb.append(row)
        
        return kb
