from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data, formatar_cpf, formatar_telefone
from typing import Optional, List, Dict
from datetime import datetime

class ClienteModel:
    
    @staticmethod
    def get_by_telegram(telegram_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_id(cliente_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_cpf(cpf: str) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM clientes WHERE cpf = ?', (cpf,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def criar(telegram_id: int, dados: Dict = None) -> Dict:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO clientes (telegram_id, nome, sobrenome, etapa_cadastro, data_cadastro)
            VALUES (?, ?, ?, 'inicio', datetime('now'))
        ''', (telegram_id, dados.get('nome', '') if dados else '', dados.get('sobrenome', '') if dados else ''))
        db.commit()
        return {'id': cursor.lastrowid, 'telegram_id': telegram_id}
    
    @staticmethod
    def atualizar(cliente_id: int, dados: Dict) -> bool:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['nome', 'sobrenome', 'email', 'telefone', 'cpf', 'cnpj', 
                     'data_nascimento', 'sexo', 'razao_social', 'nome_fantasia',
                     'inscricao_estadual', 'responsavel']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return False
        
        valores.append(cliente_id)
        db.execute(f'UPDATE clientes SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return True
    
    @staticmethod
    def verificar(cliente_id: int) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET verificado = 1, codigo_verificacao = NULL, etapa_cadastro = ? WHERE id = ?',
                   ('completo', cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def bloquear(cliente_id: int) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET bloqueado = 1 WHERE id = ?', (cliente_id,))
        db.commit()
        return True
    
    @staticmethod
    def desbloquear(cliente_id: int) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET bloqueado = 0 WHERE id = ?', (cliente_id,))
        db.commit()
        return True
    
    @staticmethod
    def adicionar_saldo(cliente_id: int, valor: float) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET saldo = saldo + ? WHERE id = ?', (valor, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def adicionar_gasto(cliente_id: int, valor: float) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET total_gasto = total_gasto + ? WHERE id = ?', (valor, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def adicionar_pontos(cliente_id: int, pontos: int) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + ? WHERE id = ?', (pontos, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def adicionar_cashback(cliente_id: int, valor: float) -> bool:
        db = get_db()
        db.execute('UPDATE clientes SET cashback = cashback + ? WHERE id = ?', (valor, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def get_total_pedidos(cliente_id: int) -> int:
        db = get_db()
        return db.execute('SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ?', (cliente_id,)).fetchone()['t']
    
    @staticmethod
    def get_total_gasto(cliente_id: int) -> float:
        db = get_db()
        return db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE cliente_id = ? AND pagamento_status = 'approved'", 
                         (cliente_id,)).fetchone()['t']
    
    @staticmethod
    def listar_todos(pagina: int = 1, limite: int = 20) -> Dict:
        db = get_db()
        offset = (pagina - 1) * limite
        total = db.execute('SELECT COUNT(*) as t FROM clientes').fetchone()['t']
        clientes = [dict(r) for r in db.execute(
            'SELECT * FROM clientes ORDER BY total_gasto DESC LIMIT ? OFFSET ?',
            (limite, offset)
        ).fetchall()]
        return {'clientes': clientes, 'total': total, 'pagina': pagina}
    
    @staticmethod
    def buscar(termo: str) -> List[Dict]:
        db = get_db()
        busca = f'%{termo}%'
        return [dict(r) for r in db.execute(
            'SELECT * FROM clientes WHERE nome LIKE ? OR telefone LIKE ? OR cpf LIKE ? OR email LIKE ? LIMIT 20',
            (busca, busca, busca, busca)
        ).fetchall()]
    
    @staticmethod
    def get_ranking(limite: int = 20) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT nome, total_gasto, pontos_fidelidade FROM clientes WHERE bloqueado = 0 AND total_gasto > 0 ORDER BY total_gasto DESC LIMIT ?',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def formatar_dados(cliente: Dict) -> Dict:
        return {
            **cliente,
            'cpf_formatado': formatar_cpf(cliente.get('cpf', '')) if cliente.get('cpf') else None,
            'telefone_formatado': formatar_telefone(cliente.get('telefone', '')) if cliente.get('telefone') else None,
            'total_gasto_formatado': formatar_moeda(cliente.get('total_gasto', 0)),
            'saldo_formatado': formatar_moeda(cliente.get('saldo', 0)),
            'cashback_formatado': formatar_moeda(cliente.get('cashback', 0)),
            'data_cadastro_formatada': formatar_data(cliente.get('data_cadastro'))
        }
