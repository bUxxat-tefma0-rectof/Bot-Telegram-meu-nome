from database.connection import get_db

class MensagensAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute('SELECT * FROM mensagens_bot ORDER BY chave').fetchall()]
    
    @staticmethod
    def editar(chave: str, conteudo: str) -> dict:
        db = get_db()
        existe = db.execute('SELECT * FROM mensagens_bot WHERE chave = ?', (chave,)).fetchone()
        if existe:
            db.execute('UPDATE mensagens_bot SET conteudo = ?, data_modificacao = datetime("now") WHERE chave = ?',
                       (conteudo, chave))
        else:
            db.execute('INSERT INTO mensagens_bot (chave, conteudo) VALUES (?, ?)', (chave, conteudo))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Mensagem atualizada!'}
    
    @staticmethod
    def get_mensagem(chave: str) -> str:
        db = get_db()
        row = db.execute('SELECT conteudo FROM mensagens_bot WHERE chave = ?', (chave,)).fetchone()
        return row['conteudo'] if row else ''
    
    @staticmethod
    def resetar_padrao(chave: str) -> dict:
        padroes = {
            'start': 'Bem-vindo(a) {nome} à {loja}! 🛒\n\nEscolha uma opção:',
            'cadastro_nome': '📝 Digite seu nome completo:',
            'cadastro_sucesso': '🎉 Cadastro realizado com sucesso!',
            'compra_sucesso': '✅ Pedido {numero} confirmado! Total: {total}',
            'pix_gerado': '💳 PIX gerado!\n\n📋 `{pix}`\n\n⏰ Expira em {expiracao} min',
            'pagamento_aprovado': '✅ Pagamento aprovado! Preparando seu pedido...'
        }
        
        if chave in padroes:
            return MensagensAdmin.editar(chave, padroes[chave])
        return {'sucesso': False, 'mensagem': 'Chave não encontrada'}
