from database.connection import get_db
from telegram import InlineKeyboardButton
from typing import List

class MenuService:
    
    @staticmethod
    def get_menu(menu_nome: str) -> List[List[InlineKeyboardButton]]:
        db = get_db()
        botoes = db.execute(
            "SELECT * FROM botoes_menu WHERE menu = ? AND ativo = 1 ORDER BY linha, ordem",
            (menu_nome,)
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
            elif btn['webapp_url']:
                from telegram import WebAppInfo
                row.append(InlineKeyboardButton(texto, web_app=WebAppInfo(url=btn['webapp_url'])))
            else:
                row.append(InlineKeyboardButton(texto, callback_data=btn['callback_data']))
        
        if row:
            kb.append(row)
        
        return kb
    
    @staticmethod
    def criar_menu(nome: str, botoes: list) -> dict:
        db = get_db()
        try:
            for i, btn in enumerate(botoes):
                db.execute('''
                    INSERT INTO botoes_menu (menu, texto, emoji, callback_data, url, ordem, linha)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (nome, btn['texto'], btn.get('emoji',''), btn.get('callback',''), 
                      btn.get('url',''), i+1, btn.get('linha',1)))
            db.commit()
            return {'sucesso': True, 'mensagem': f'Menu {nome} criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def deletar_menu(nome: str):
        db = get_db()
        db.execute("DELETE FROM botoes_menu WHERE menu = ?", (nome,))
        db.commit()
    
    @staticmethod
    def listar_menus() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT DISTINCT menu FROM botoes_menu ORDER BY menu"
        ).fetchall()]
