import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.geral import Config
import logging

logger = logging.getLogger(__name__)

class EmailService:
    
    @staticmethod
    def enviar(destinatario: str, assunto: str, mensagem: str) -> dict:
        try:
            remetente = Config.EMAIL_REMETENTE if hasattr(Config, 'EMAIL_REMETENTE') else 'loja@digital.com'
            
            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = assunto
            
            msg.attach(MIMEText(mensagem, 'html'))
            
            logger.info(f'Email enviado para {destinatario}')
            return {'sucesso': True, 'mensagem': 'Email enviado!'}
        except Exception as e:
            logger.error(f'Erro email: {e}')
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def enviar_codigo_verificacao(destinatario: str, codigo: str) -> dict:
        assunto = f'{Config.NOME_LOJA} - Código de Verificação'
        mensagem = f'''
        <div style="text-align:center; font-family:Arial;">
            <h1 style="color:{Config.get('cor_primaria', '#6366f1')};">{Config.NOME_LOJA}</h1>
            <p>Seu código de verificação é:</p>
            <h2 style="background:#f0f0f0; padding:15px; border-radius:10px; display:inline-block;">{codigo}</h2>
            <p>Válido por 10 minutos</p>
        </div>
        '''
        return EmailService.enviar(destinatario, assunto, mensagem)
