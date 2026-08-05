from telegram import InputMediaPhoto, InputMediaVideofrom typing import List, Union, Dict

class MidiasService:
    
    @staticmethod
    def criar_album_fotos(fotos: List[str], caption: str = None) -> List[InputMediaPhoto]:
        media_group = []
        for i, foto in enumerate(fotos[:10]):
            if i == 0 and caption:
                media_group.append(InputMediaPhoto(media=foto, caption=caption[:1024], parse_mode='Markdown'))
            else:
                media_group.append(InputMediaPhoto(media=foto))
        return media_group
    
    @staticmethod
    def criar_album_misto(midias: List[Dict]) -> List[Union[InputMediaPhoto, InputMediaVideo]]:
        media_group = []
        for i, m in enumerate(midias[:10]):
            caption = m.get('caption', '')[:1024] if i == 0 else None
            if m.get('tipo') == 'foto':
                media_group.append(InputMediaPhoto(media=m['url'], caption=caption, parse_mode='Markdown'))
            elif m.get('tipo') == 'video':
                media_group.append(InputMediaVideo(media=m['url'], caption=caption, parse_mode='Markdown'))
        return media_group
    
    @staticmethod
    def criar_galeria_produto(produto: Dict) -> List[InputMediaPhoto]:
        fotos = []
        if produto.get('foto'):
            fotos.append(produto['foto'])
        if produto.get('galeria'):
            import json
            try:
                galeria = json.loads(produto['galeria'])
                if isinstance(galeria, list):
                    fotos.extend(galeria)
            except:
                pass
        
        if not fotos:
            return []
        
        preco = produto.get('preco_promocional') or produto.get('preco', 0)
        caption = f'📦 *{produto["nome"]}*\n'
        if produto.get('marca'):
            caption += f'🏷 {produto["marca"]}\n'
        caption += f'💰 R$ {preco:,.2f}'
        
        return MidiasService.criar_album_fotos(fotos[:10], caption)
    
    @staticmethod
    def get_tipo_midia(file_id: str) -> str:
        if file_id.startswith('AgAC'):
            return 'foto'
        elif file_id.startswith('BAAC'):
            return 'video'
        elif file_id.startswith('CQAC'):
            return 'audio'
        elif file_id.startswith('BQAC'):
            return 'documento'
        return 'desconhecido'
