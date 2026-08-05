from telegram import InputMediaPhoto, InputMediaVideo
from typing import List, Union

class MidiasService:
    
    @staticmethod
    def criar_album(fotos: List[str], caption: str = None) -> List[InputMediaPhoto]:
        """Cria um álbum de fotos"""
        media_group = []
        for i, foto in enumerate(fotos):
            if i == 0 and caption:
                media_group.append(InputMediaPhoto(media=foto, caption=caption[:1024], parse_mode='Markdown'))
            else:
                media_group.append(InputMediaPhoto(media=foto))
        return media_group
    
    @staticmethod
    def criar_album_misto(midias: List[dict]) -> List[Union[InputMediaPhoto, InputMediaVideo]]:
        """Cria um álbum com fotos e vídeos"""
        media_group = []
        for i, m in enumerate(midias):
            caption = m.get('caption', '')[:1024] if i == 0 else None
            if m['tipo'] == 'foto':
                media_group.append(InputMediaPhoto(media=m['url'], caption=caption, parse_mode='Markdown'))
            elif m['tipo'] == 'video':
                media_group.append(InputMediaVideo(media=m['url'], caption=caption, parse_mode='Markdown'))
        return media_group
    
    @staticmethod
    def criar_galeria_produto(produto: dict) -> List[InputMediaPhoto]:
        """Cria galeria para um produto"""
        fotos = []
        if produto.get('foto'):
            fotos.append(produto['foto'])
        if produto.get('galeria'):
            try:
                import json
                galeria = json.loads(produto['galeria'])
                fotos.extend(galeria)
            except:
                pass
        
        caption = f'📦 *{produto["nome"]}*\n💰 {produto["preco"]}'
        return MidiasService.criar_album(fotos[:10], caption)
