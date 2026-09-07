"""Compõe as molduras aprovadas sobre as animações, sem perda de pixels.

Executar da raiz do repositório: python scripts/compor-molduras-perfil.py
Dependências: Pillow e NumPy. Não modifica nenhum arquivo de origem.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import struct
import time
import numpy as np
from PIL import Image, ImageChops

RAIZ = Path(__file__).resolve().parents[1]
ASSETS = RAIZ / 'assets/v3'
CONFIGURACOES = {
    'topo': dict(origem='banner/banner-animado.webp', moldura='frame/frame-top.png',
                 tela=(2320, 846), tamanho_moldura=(2320, 360), posicao_moldura=(0, 0),
                 posicao_animacao=(74, 122), escala_inteira=1, destino='banner/banner-emoldurado.webp'),
    'rodape': dict(origem='footer/vergil-animado.webp', moldura='frame/frame-bottom.png',
                  tela=(2560, 627), tamanho_moldura=(2560, 401), posicao_moldura=(0, 226),
                  posicao_animacao=(80, 0), escala_inteira=2, destino='footer/vergil-emoldurado.webp'),
}

def blocos(dados):
    indice = 12
    while indice < len(dados):
        tamanho = int.from_bytes(dados[indice+4:indice+8], 'little')
        yield dados[indice:indice+4], dados[indice+8:indice+8+tamanho]
        indice += 8 + tamanho + tamanho % 2

def bloco(tipo, dados):
    return tipo + struct.pack('<I', len(dados)) + dados + b'\0' * (len(dados) % 2)

def inteiro24(valor):
    return valor.to_bytes(3, 'little')

def assinatura(imagem):
    return hashlib.sha256(imagem.tobytes()).hexdigest()

def compor(nome):
    configuracao = CONFIGURACOES[nome]
    origem = ASSETS / configuracao['origem']
    destino = ASSETS / configuracao['destino']
    dados = origem.read_bytes()
    tempos = [int.from_bytes(conteudo[12:15], 'little')
              for tipo, conteudo in blocos(dados) if tipo == b'ANMF']
    animacao = Image.open(origem)
    assert len(tempos) == animacao.n_frames
    moldura = Image.open(ASSETS / configuracao['moldura']).convert('RGBA')
    # Somente a moldura é ampliada proporcionalmente; não há interpolação nem blur.
    moldura = moldura.resize(configuracao['tamanho_moldura'], Image.Resampling.NEAREST)
    largura, altura = configuracao['tela']
    perfil = animacao.info.get('icc_profile')
    repeticoes = animacao.info.get('loop', 0)
    esperado = []
    anterior = None
    inicio = time.monotonic()
    with destino.open('wb') as arquivo:
        arquivo.write(b'RIFF\0\0\0\0WEBP')
        # VP8X: animação e transparência; perfil de cor quando presente na origem.
        arquivo.write(bloco(b'VP8X', bytes([0x12 | (0x20 if perfil else 0)]) + b'\0'*3
                            + inteiro24(largura-1) + inteiro24(altura-1)))
        if perfil:
            arquivo.write(bloco(b'ICCP', perfil))
        arquivo.write(bloco(b'ANIM', b'\0'*4 + struct.pack('<H', repeticoes)))
        for indice, duracao in enumerate(tempos):
            animacao.seek(indice)
            quadro = animacao.convert('RGBA')
            escala = configuracao['escala_inteira']
            if escala != 1:
                # Duplicação exata 2x: cada pixel original vira um bloco 2x2, sem perda.
                quadro = quadro.resize((quadro.width*escala, quadro.height*escala), Image.Resampling.NEAREST)
            atual = Image.new('RGBA', (largura, altura))
            atual.alpha_composite(quadro, configuracao['posicao_animacao'])
            atual.alpha_composite(moldura, configuracao['posicao_moldura'])
            esperado.append(assinatura(atual))
            if anterior is None:
                caixa = (0, 0, largura, altura)
                recorte = atual
                flags = 2  # Primeiro quadro substitui a tela inteira.
                atual.save(destino.with_name(destino.stem+'-estatico.png'), optimize=True)
            else:
                caixa = ImageChops.difference(atual, anterior).getbbox(alpha_only=False)
                if caixa is None:
                    caixa = (0, 0, 1, 1)
                    recorte = Image.new('RGBA', (1, 1))
                else:
                    # O contêiner WebP representa as posições em unidades de 2 pixels.
                    caixa = (caixa[0]//2*2, caixa[1]//2*2, caixa[2], caixa[3])
                    novo = np.array(atual.crop(caixa))
                    antigo = np.array(anterior.crop(caixa))
                    mudou = np.any(novo != antigo, axis=2)
                    assert np.all(novo[:, :, 3][mudou] == 255), 'Mudança semitransparente inesperada'
                    novo[~mudou] = 0
                    recorte = Image.fromarray(novo)
                flags = 0  # Transparência preserva os pixels que não mudaram.
            buffer = BytesIO()
            recorte.save(buffer, format='WEBP', lossless=True, exact=True, method=4)
            dados_quadro = b''.join(bloco(tipo, conteudo) for tipo, conteudo in blocos(buffer.getvalue())
                                   if tipo in (b'ALPH', b'VP8 ', b'VP8L'))
            cabecalho = (inteiro24(caixa[0]//2) + inteiro24(caixa[1]//2)
                         + inteiro24(recorte.width-1) + inteiro24(recorte.height-1)
                         + inteiro24(duracao) + bytes([flags]))
            arquivo.write(bloco(b'ANMF', cabecalho + dados_quadro))
            anterior = atual
            if indice % 50 == 0:
                print(f'{nome}: {indice+1}/{len(tempos)} quadros; {arquivo.tell()/1048576:.1f} MiB', flush=True)
        tamanho = arquivo.tell()
        arquivo.seek(4)
        arquivo.write(struct.pack('<I', tamanho-8))
    assert tamanho < 100*1048576, 'Arquivo excede o limite de 100 MiB do GitHub'
    # Decodificação independente para conferir TODOS os quadros após a gravação.
    resultado = Image.open(destino)
    assert resultado.n_frames == len(tempos)
    assert resultado.info.get('loop', 0) == repeticoes
    for indice, resumo in enumerate(esperado):
        resultado.seek(indice)
        assert assinatura(resultado.convert('RGBA')) == resumo, f'Diferença visual no quadro {indice}'
    tempos_resultado = [int.from_bytes(conteudo[12:15], 'little')
                       for tipo, conteudo in blocos(destino.read_bytes()) if tipo == b'ANMF']
    assert tempos_resultado == tempos
    relatorio = dict(configuracao, quadros=len(tempos), duracao_ms=sum(tempos),
                     repeticoes=repeticoes, bytes=tamanho,
                     sha256_origem=hashlib.sha256(dados).hexdigest(),
                     sha256_resultado=hashlib.sha256(destino.read_bytes()).hexdigest(),
                     verificacao='Todos os quadros decodificados são idênticos à composição sem perdas; tempos e repetição preservados.')
    destino.with_suffix('.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{nome}: concluído e verificado em {time.monotonic()-inicio:.0f}s; {tamanho/1048576:.2f} MiB', flush=True)

if __name__ == '__main__':
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument('parte', choices=['topo', 'rodape', 'ambos'], default='ambos', nargs='?')
    parte = argumentos.parse_args().parte
    for nome in CONFIGURACOES if parte == 'ambos' else [parte]:
        compor(nome)
