import csv
import json
from database.connection import get_db
from io import StringIO
import logging

logger = logging.getLogger(__name__)

class ExportacaoService:
    
    @staticmethod
    def exportar_produtos_csv() -> dict:
        try:
            db = get_db()
            produtos = db.execute('SELECT * FROM produtos').fetchall()
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Nome', 'Categoria', 'Preço', 'Estoque', 'Marca'])
            
            for p in produtos:
                writer.writerow([p['id'], p['nome'], p.get('categoria_id',''), p['preco'], p['estoque'], p.get('marca','')])
            
            return {'sucesso': True, 'dados': output.getvalue()}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def exportar_pedidos_csv() -> dict:
        try:
            db = get_db()
            pedidos = db.execute('''
                SELECT p.*, c.nome, c.telefone 
                FROM pedidos p 
                JOIN clientes c ON p.cliente_id = c.id 
                ORDER BY p.data_pedido DESC
            ''').fetchall()
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Número', 'Cliente', 'Telefone', 'Total', 'Status', 'Data'])
            
            for p in pedidos:
                writer.writerow([p['numero'], p['nome'], p.get('telefone',''), p['total'], p['status'], p['data_pedido']])
            
            return {'sucesso': True, 'dados': output.getvalue()}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def exportar_clientes_csv() -> dict:
        try:
            db = get_db()
            clientes = db.execute('SELECT * FROM clientes ORDER BY total_gasto DESC').fetchall()
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Nome', 'Telefone', 'Email', 'Total Gasto', 'Pontos'])
            
            for c in clientes:
                writer.writerow([c['telegram_id'], c['nome'], c.get('telefone',''), c.get('email',''), c['total_gasto'], c['pontos_fidelidade']])
            
            return {'sucesso': True, 'dados': output.getvalue()}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
