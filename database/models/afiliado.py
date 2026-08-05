from database.connection import get_db
from typing import List, Dict, Optional
from utils.helpers import gerar_codigo_afiliado

class AfiliadoModel:
    
    @staticmethod
    def get_by_cliente(cliente_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM afiliados WHERE cliente_id = ?', (cliente_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_id(afiliado_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM afiliados WHERE id = ?', (afiliado_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM afiliados WHERE codigo = ? AND ativo = 1', (codigo,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def criar(cliente_id: int, nome: str = '') -> Dict:
        db = get_db()
        
        existe = db.execute('SELECT * FROM afiliados WHERE cliente_id = ?', (cliente_id,)).fetchone()
        if existe:
            return {'sucesso': True, 'afiliado': dict(existe)}
        
        codigo = gerar_codigo_afiliado(nome or f'CLI{cliente_id}')
        
        try:
            cursor = db.execute('''
                INSERT INTO afiliados (cliente_id, codigo, comissao_percentual, nivel, ativo)
                VALUES (?, ?, 5, 1, 1)
            ''', (cliente_id, codigo))
            db.commit()
            
            return {
                'sucesso': True,
                'afiliado': {
                    'id': cursor.lastrowid,
                    'cliente_id': cliente_id,
                    'codigo': codigo,
                    'comissao_percentual': 5,
                    'nivel': 1
                }
            }
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def processar_indicacao(codigo: str, novo_cliente_id: int) -> bool:
        afiliado = AfiliadoModel.get_by_codigo(codigo)
        if not afiliado:
            return False
        
        db = get_db()
        db.execute('UPDATE clientes SET afiliado_id = ? WHERE id = ?',
                   (afiliado['id'], novo_cliente_id))
        db.execute('UPDATE afiliados SET total_indicacoes = total_indicacoes + 1 WHERE id = ?',
                   (afiliado['id'],))
        db.commit()
        return True
    
    @staticmethod
    def adicionar_comissao(afiliado_id: int, pedido_id: int, valor: float) -> bool:
        db = get_db()
        db.execute('''
            INSERT INTO comissoes (afiliado_id, pedido_id, valor, status, data)
            VALUES (?, ?, ?, 'aprovado', datetime('now'))
        ''', (afiliado_id, pedido_id, valor))
        db.execute('''
            UPDATE afiliados SET total_comissoes = total_comissoes + ?, saldo_comissao = saldo_comissao + ?
            WHERE id = ?
        ''', (valor, valor, afiliado_id))
        db.commit()
        return True
    
    @staticmethod
    def solicitar_saque(afiliado_id: int, valor: float) -> Dict:
        db = get_db()
        afiliado = db.execute('SELECT saldo_comissao FROM afiliados WHERE id = ?', (afiliado_id,)).fetchone()
        
        if not afiliado:
            return {'sucesso': False, 'mensagem': 'Afiliado não encontrado'}
        if afiliado['saldo_comissao'] < valor:
            return {'sucesso': False, 'mensagem': 'Saldo insuficiente'}
        if valor < 50:
            return {'sucesso': False, 'mensagem': 'Valor mínimo para saque: R$ 50,00'}
        
        db.execute('''
            INSERT INTO comissoes (afiliado_id, valor, status, data)
            VALUES (?, ?, 'pendente', datetime('now'))
        ''', (afiliado_id, -valor))
        db.execute('UPDATE afiliados SET saldo_comissao = saldo_comissao - ? WHERE id = ?',
                   (valor, afiliado_id))
        db.commit()
        
        return {'sucesso': True, 'mensagem': f'Saque de R$ {valor:.2f} solicitado! Processado em até 7 dias.'}
    
    @staticmethod
    def aprovar_saque(comissao_id: int) -> bool:
        db = get_db()
        db.execute("UPDATE comissoes SET status = 'aprovado' WHERE id = ?", (comissao_id,))
        db.commit()
        return True
    
    @staticmethod
    def editar_comissao(afiliado_id: int, percentual: float) -> bool:
        db = get_db()
        db.execute('UPDATE afiliados SET comissao_percentual = ? WHERE id = ?', (percentual, afiliado_id))
        db.commit()
        return True
    
    @staticmethod
    def toggle(afiliado_id: int) -> bool:
        db = get_db()
        a = db.execute('SELECT ativo FROM afiliados WHERE id = ?', (afiliado_id,)).fetchone()
        if not a:
            return False
        novo = 0 if a['ativo'] else 1
        db.execute('UPDATE afiliados SET ativo = ? WHERE id = ?', (novo, afiliado_id))
        db.commit()
        return True
    
    @staticmethod
    def listar_todos() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT a.*, c.nome, c.telefone, c.email, c.total_gasto
               FROM afiliados a JOIN clientes c ON a.cliente_id = c.id
               ORDER BY a.total_comissoes DESC'''
        ).fetchall()]
    
    @staticmethod
    def get_ranking(limite: int = 20) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT a.*, c.nome FROM afiliados a
               JOIN clientes c ON a.cliente_id = c.id
               WHERE a.ativo = 1 ORDER BY a.total_comissoes DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_indicados(afiliado_id: int) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT nome, total_gasto, pontos_fidelidade, data_cadastro FROM clientes WHERE afiliado_id = ?',
            (afiliado_id,)
        ).fetchall()]
    
    @staticmethod
    def get_comissoes(afiliado_id: int) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM comissoes WHERE afiliado_id = ? ORDER BY data DESC',
            (afiliado_id,)
        ).fetchall()]
