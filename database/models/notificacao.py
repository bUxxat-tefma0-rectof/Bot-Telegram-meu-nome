from database.connection import get_db
from typing import List, Dict, Optional
from datetime import datetime

class NotificacaoModel:
    
    TIPOS = ['info', 'pedido', 'pagamento', 'promocao', 'estoque', 'aniversario', 'admin', 'alerta']
    
    @staticmethod
    def criar(cliente_id: int, tipo: str, titulo: str, mensagem: str) -> int:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO notificacoes (cliente_id, tipo, titulo, mensagem, lida, data)
            VALUES (?, ?, ?, ?, 0, datetime('now'))
        ''', (cliente_id, tipo, titulo, mensagem))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_nao_lidas(cliente_id: int) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM notificacoes WHERE cliente_id = ? AND lida = 0 ORDER BY data DESC',
            (cliente_id,)
        ).fetchall()]
    
    @staticmethod
    def get_todas(cliente_id: int, limite: int = 50) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM notificacoes WHERE cliente_id = ? ORDER BY data DESC LIMIT ?',
            (cliente_id, limite)
        ).fetchall()]
    
    @staticmethod
    def marcar_como_lida(notificacao_id: int, cliente_id: int = None) -> bool:
        db = get_db()
        if cliente_id:
            db.execute('UPDATE notificacoes SET lida = 1 WHERE id = ? AND cliente_id = ?',
                       (notificacao_id, cliente_id))
        else:
            db.execute('UPDATE notificacoes SET lida = 1 WHERE id = ?', (notificacao_id,))
        db.commit()
        return True
    
    @staticmethod
    def marcar_todas_como_lidas(cliente_id: int) -> bool:
        db = get_db()
        db.execute('UPDATE notificacoes SET lida = 1 WHERE cliente_id = ? AND lida = 0',
                   (cliente_id,))
        db.commit()
        return True
    
    @staticmethod
    def contar_nao_lidas(cliente_id: int) -> int:
        db = get_db()
        result = db.execute(
            'SELECT COUNT(*) as t FROM notificacoes WHERE cliente_id = ? AND lida = 0',
            (cliente_id,)
        ).fetchone()
        return result['t'] if result else 0
    
    @staticmethod
    def limpar_antigas(dias: int = 30) -> int:
        db = get_db()
        result = db.execute(f"DELETE FROM notificacoes WHERE data < datetime('now', '-{dias} days')")
        db.commit()
        return result.rowcount
    
    @staticmethod
    def criar_para_todos(tipo: str, titulo: str, mensagem: str) -> int:
        db = get_db()
        clientes = db.execute('SELECT id FROM clientes WHERE bloqueado = 0').fetchall()
        count = 0
        for c in clientes:
            NotificacaoModel.criar(c['id'], tipo, titulo, mensagem)
            count += 1
        return count
    
    @staticmethod
    def criar_para_grupo(grupo: str, tipo: str, titulo: str, mensagem: str) -> int:
        db = get_db()
        
        if grupo == 'afiliados':
            clientes = db.execute('SELECT cliente_id as id FROM afiliados WHERE ativo = 1').fetchall()
        elif grupo == 'inativos':
            clientes = db.execute("SELECT id FROM clientes WHERE ultimo_acesso < datetime('now', '-30 days')").fetchall()
        elif grupo == 'vips':
            clientes = db.execute('SELECT id FROM clientes WHERE total_gasto > 1000').fetchall()
        else:
            clientes = db.execute('SELECT id FROM clientes WHERE bloqueado = 0').fetchall()
        
        count = 0
        for c in clientes:
            NotificacaoModel.criar(c['id'], tipo, titulo, mensagem)
            count += 1
        return count
