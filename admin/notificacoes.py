from database.connection import get_db
from services.notificacoes import NotificacaoService
from datetime import datetime

class NotificacoesAdmin:
    
    @staticmethod
    def listar(limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM notificacoes ORDER BY data DESC LIMIT ?', (limite,)
        ).fetchall()]
    
    @staticmethod
    def enviar_para_todos(titulo: str, mensagem: str) -> dict:
        NotificacaoService.notificar_promocao(mensagem)
        return {'sucesso': True, 'mensagem': 'Notificação enviada para todos!'}
    
    @staticmethod
    def enviar_para_cliente(cliente_id: int, titulo: str, mensagem: str) -> dict:
        NotificacaoService.enviar(cliente_id, 'admin', titulo, mensagem)
        return {'sucesso': True, 'mensagem': 'Notificação enviada!'}
    
    @staticmethod
    def enviar_para_grupo(grupo: str, titulo: str, mensagem: str) -> dict:
        db = get_db()
        
        if grupo == 'clientes':
            clientes = db.execute('SELECT id FROM clientes WHERE bloqueado = 0').fetchall()
        elif grupo == 'afiliados':
            clientes = db.execute('SELECT cliente_id as id FROM afiliados WHERE ativo = 1').fetchall()
        elif grupo == 'inativos':
            clientes = db.execute("SELECT id FROM clientes WHERE ultimo_acesso < datetime('now', '-30 days')").fetchall()
        else:
            return {'sucesso': False, 'mensagem': 'Grupo inválido'}
        
        for c in clientes:
            NotificacaoService.enviar(c['id'], 'admin', titulo, mensagem)
        
        return {'sucesso': True, 'mensagem': f'Enviado para {len(clientes)} pessoas'}
    
    @staticmethod
    def agendar(data_hora: str, titulo: str, mensagem: str, grupo: str = 'todos') -> dict:
        from services.scheduler import SchedulerService
        scheduler = SchedulerService()
        scheduler.agendar_notificacao(data_hora, titulo, mensagem, grupo)
        return {'sucesso': True, 'mensagem': f'Notificação agendada para {data_hora}'}
