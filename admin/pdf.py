from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from utils.helpers import formatar_moeda, formatar_data

class PDFService:
    
    @staticmethod
    def gerar_relatorio(pedidos: list, itens: list) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        
        elementos = []
        
        # Título
        title_style = ParagraphStyle('Title', fontSize=20, alignment=1, spaceAfter=20)
        elementos.append(Paragraph('Relatório de Vendas', title_style))
        elementos.append(Paragraph(f'Gerado em: {formatar_data(__import__("datetime").datetime.now())}', styles['Normal']))
        elementos.append(Spacer(1, 20))
        
        # Tabela
        data = [['Pedido', 'Cliente', 'Data', 'Valor', 'Status']]
        for p in pedidos:
            data.append([
                p['numero'],
                p.get('nome', 'N/A')[:20],
                formatar_data(p['data_pedido']),
                formatar_moeda(p['total']),
                p['status']
            ])
        
        table = Table(data, colWidths=[80, 120, 100, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        elementos.append(table)
        elementos.append(Spacer(1, 20))
        
        # Total
        total = sum(p['total'] for p in pedidos)
        elementos.append(Paragraph(f'Total: {formatar_moeda(total)}', styles['Heading3']))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer.getvalue()
