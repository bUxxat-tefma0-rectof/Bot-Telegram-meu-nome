from database.connection import get_db
import json

class WebhooksAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM configuracoes WHERE chave LIKE 'webhook_%'"
        ).fetchall()]
    
    @staticmethod
    def criar(url: str, eventos: list, ativo: bool = True) -> dict:
        db = get_db()
        chave = f"webhook_{len(WebhooksAdmin.listar()) + 1}"
        
        dados = json.dumps({'url': url, 'eventos': eventos, 'ativo': ativo})
        
        db.execute("INSERT INTO configuracoes (chave, valor, categoria) VALUES (?, ?, 'webhooks')",
                   (chave, dados))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Webhook criado!'}
    
    @staticmethod
    def editar(webhook_id: int, dados: dict) -> dict:
        db = get_db()
        webhook = db.execute('SELECT * FROM configuracoes WHERE id = ?', (webhook_id,)).fetchone()
        if not webhook:
            return {'sucesso': False, 'mensagem': 'Webhook não encontrado'}
        
        config = json.loads(webhook['valor'])
        config.update(dados)
        
        db.execute('UPDATE configuracoes SET valor = ? WHERE id = ?', (json.dumps(config), webhook_id))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Webhook atualizado!'}
    
    @staticmethod
    def excluir(webhook_id: int):
        db = get_db()
        db.execute('DELETE FROM configuracoes WHERE id = ?', (webhook_id,))
        db.commit()
    
    @staticmethod
    def testar(url: str) -> dict:
        import requests
        try:
            resp = requests.post(url, json={'teste': True, 'data': 'Webhook test'}, timeout=5)
            return {'sucesso': True, 'status': resp.status_code, 'resposta': resp.text[:200]}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
