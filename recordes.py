"""Sistema de high score: guarda as melhores pontuações num arquivo JSON.

Cada recorde é um dicionário {"nome": "ABC", "pontos": 42}. A lista fica sempre
ordenada da maior para a menor pontuação e com no máximo TAMANHO_RANKING itens.
"""

import json
import os

TAMANHO_RANKING = 5
TAMANHO_NOME = 3  # iniciais, no estilo dos fliperamas

# Caminho relativo a este arquivo, para o JSON ficar junto do jogo
# independentemente da pasta de onde o "python main.py" foi executado.
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordes.json")


def carregar():
    """Lê os recordes do arquivo. Se ele não existir ou estiver corrompido, começa vazio."""
    try:
        with open(ARQUIVO, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        recordes = [
            {"nome": str(r["nome"])[:TAMANHO_NOME], "pontos": int(r["pontos"])}
            for r in dados
        ]
    except (OSError, ValueError, TypeError, KeyError):
        return []
    recordes.sort(key=lambda r: r["pontos"], reverse=True)
    return recordes[:TAMANHO_RANKING]


def salvar(recordes):
    """Grava os recordes no arquivo. Se não conseguir gravar, o jogo segue sem travar."""
    try:
        with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
            json.dump(recordes, arquivo, ensure_ascii=False, indent=2)
    except OSError:
        pass


def entra_no_ranking(recordes, pontos):
    """True se essa pontuação merece um lugar na tabela."""
    if pontos <= 0:
        return False
    if len(recordes) < TAMANHO_RANKING:
        return True
    # Precisa ser MAIOR que o último: em caso de empate, quem chegou antes fica.
    return pontos > recordes[-1]["pontos"]


def adicionar(recordes, nome, pontos):
    """Coloca o novo recorde na lista (já ordenada) e devolve a posição dele (0 = 1º)."""
    novo = {"nome": nome, "pontos": pontos}
    recordes.append(novo)
    # sort() é estável: num empate, o recorde novo fica abaixo dos antigos.
    recordes.sort(key=lambda r: r["pontos"], reverse=True)
    del recordes[TAMANHO_RANKING:]
    # "is" compara identidade, para achar exatamente o recorde novo.
    for posicao, recorde in enumerate(recordes):
        if recorde is novo:
            return posicao
    return None


def melhor(recordes):
    """Maior pontuação já feita (0 se ainda não há recordes)."""
    return recordes[0]["pontos"] if recordes else 0
