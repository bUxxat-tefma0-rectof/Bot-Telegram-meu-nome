from database.connection import get_db

class BotoesAdmin:
    
    @staticmethod
    def listar(menu: str = None) -> list:
        db = get_db()
        if menu:
            return [dict(r) for r in db.execute(
                'SELECT * FROM botoes_menu WHERE menu = ? ORDER BY linha, ordem', (menu,)
            ).fetchall()]
        return [dict(r) for r in db.execute(
            'SELECT * FROM botoes_menu ORDER BY menu, linha, ordem'
        ).fetchall()]
    
    @staticmethod
    def criar(menu: str, texto: str, callback: str = None, url: str = None,
              emoji: str = None, ordem: int = 1, linha: int = 1, admin_only: int = 0) -> dict:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO botoes_menu (menu, texto, emoji, callback_data, url, ordem, linha, admin_only)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (menu, texto, emoji, callback, url, ordem, linha, admin_only))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Botão criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def editar(botao_id: int, dados: dict) -> dict:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['texto', 'emoji', 'callback_data', 'url', 'webapp_url', 'ordem', 'linha', 'ativo', 'admin_only', 'menu']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return {'sucesso': False, 'mensagem': 'Nenhum dado para atualizar'}
        
        valores.append(botao_id)
        db.execute(f'UPDATE botoes_menu SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return {'sucesso': True, 'mensagem': 'Botão atualizado!'}
    
    @staticmethod
    def excluir(botao_id: int):
        db = get_db()
        db.execute('DELETE FROM botoes_menu WHERE id = ?', (botao_id,))
        db.commit()
    
    @staticmethod
    def toggle(botao_id: int) -> dict:
        db = get_db()
        btn = db.execute('SELECT ativo FROM botoes_menu WHERE id = ?', (botao_id,)).fetchone()
        if not btn:
            return {'sucesso': False}
        novo = 0 if btn['ativo'] else 1
        db.execute('UPDATE botoes_menu SET ativo = ? WHERE id = ?', (novo, botao_id))
        db.commit()
        return {'sucesso': True, 'ativo': novo}
    
    @staticmethod
    def reordenar(botoes: list) -> dict:
        db = get_db()
        for i, btn in enumerate(botoes):
            db.execute('UPDATE botoes_menu SET ordem = ?, linha = ? WHERE id = ?',
                       (btn.get('ordem', i+1), btn.get('linha', 1), btn['id']))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Ordem atualizada!'}
    
    @staticmethod
    def duplicar_menu(menu_origem: str, menu_destino: str) -> dict:
        db = get_db()
        botoes = db.execute('SELECT * FROM botoes_menu WHERE menu = ?', (menu_origem,)).fetchall()
        for btn in botoes:
            db.execute('''
                INSERT INTO botoes_menu (menu, texto, emoji, callback_data, url, ordem, linha, admin_only)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (menu_destino, btn['texto'], btn['emoji'], btn['callback_data'],
                  btn['url'], btn['ordem'], btn['linha'], btn['admin_only']))
        db.commit()
        return {'sucesso': True, 'mensagem': f'{len(botoes)} botões duplicados!'}
