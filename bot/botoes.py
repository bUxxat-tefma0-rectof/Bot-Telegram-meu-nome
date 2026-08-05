from database.connection import get_db

class BotoesService:
    
    @staticmethod
    def criar_botao(menu: str, texto: str, callback: str = None, url: str = None, 
                    emoji: str = None, ordem: int = 1, linha: int = 1) -> dict:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO botoes_menu (menu, texto, emoji, callback_data, url, ordem, linha)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (menu, texto, emoji, callback, url, ordem, linha))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Botão criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def editar_botao(botao_id: int, dados: dict) -> dict:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['texto', 'emoji', 'callback_data', 'url', 'ordem', 'linha', 'ativo']
        
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
    def deletar_botao(botao_id: int):
        db = get_db()
        db.execute('DELETE FROM botoes_menu WHERE id = ?', (botao_id,))
        db.commit()
    
    @staticmethod
    def toggle_botao(botao_id: int) -> dict:
        db = get_db()
        btn = db.execute('SELECT ativo FROM botoes_menu WHERE id = ?', (botao_id,)).fetchone()
        if not btn:
            return {'sucesso': False, 'mensagem': 'Botão não encontrado'}
        novo = 0 if btn['ativo'] else 1
        db.execute('UPDATE botoes_menu SET ativo = ? WHERE id = ?', (novo, botao_id))
        db.commit()
        return {'sucesso': True, 'ativo': novo}
    
    @staticmethod
    def get_todos_botoes() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM botoes_menu ORDER BY menu, linha, ordem'
        ).fetchall()]
