import pygame
import sys
import time
import random
import os

pygame.init()

# ================= CONFIGURAÇÕES =================
LARGURA, ALTURA = 900, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Adivinhe a Bandeira")
clock = pygame.time.Clock()

# ================= CORES =================
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
BRONZE = (205, 127, 50)
PRATA = (192, 192, 192)
OURO = (255, 215, 0)

# ================= FONTES =================
fonte = pygame.font.SysFont("arial", 24)
fonte_titulo = pygame.font.SysFont("arial", 40)

# ================= ESTADOS =================
MENU = 0
MODOS = 1
QUIZ = 2
RESULTADO = 3
TELA_CONQUISTAS = 4
estado = MENU

# ================= CONQUISTAS =================
acertos_totais = 0
medalha_bronze = False
medalha_prata = False
medalha_ouro = False

# ================= CONTROLE =================
modo = ""
indice = 0
imagem_resultado = None

# ================= TEMPO =================
TEMPO_MAX = 10
inicio_tempo = 0

# ================= FUNÇÃO IMAGEM =================
def carregar_imagem(caminho, tamanho):
    return pygame.transform.scale(
        pygame.image.load(caminho).convert_alpha(),
        tamanho
    )

# ================= LAYOUT =================
fundo_menu = carregar_imagem("layout/FUNDO DO JOGO.png", (LARGURA, ALTURA))
fundo_quiz = carregar_imagem("layout/FUNDO DO JOGO 2.png", (LARGURA, ALTURA))
img_acerto = carregar_imagem("layout/ACERTO.png", (400, 200))
img_erro = carregar_imagem("layout/ERRO.png", (400, 200))

# ================= PEGAR SIGLAS =================
def pegar_siglas_da_pasta(pasta):
    siglas = []
    extensoes = []
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            nome, ext = os.path.splitext(arquivo)
            siglas.append(nome)
            extensoes.append(ext)
    return siglas, extensoes

estados_siglas, estados_ext = pegar_siglas_da_pasta("Estados Brasileiros")
paises_siglas, paises_ext = pegar_siglas_da_pasta("Países")
times_siglas, times_ext = pegar_siglas_da_pasta("Times de Futebol")

# ================= GERAR PERGUNTAS =================
def gerar_perguntas(siglas, pasta, extensoes):
    perguntas = []
    for i, sigla in enumerate(siglas):
        imagem = carregar_imagem(f"{pasta}/{sigla}{extensoes[i]}", (400, 250))
        opcoes = random.sample(siglas, min(4, len(siglas)))
        if sigla not in opcoes:
            opcoes[0] = sigla
        random.shuffle(opcoes)

        letras = ["A", "B", "C", "D"]
        perguntas.append({
            "imagem": imagem,
            "opcoes": [f"{letras[i]} - {opcoes[i]}" for i in range(len(opcoes))],
            "resposta": letras[opcoes.index(sigla)]
        })
    random.shuffle(perguntas)
    return perguntas

perguntas = {
    "Estados": gerar_perguntas(estados_siglas, "Estados Brasileiros", estados_ext),
    "Países": gerar_perguntas(paises_siglas, "Países", paises_ext),
    "Times": gerar_perguntas(times_siglas, "Times de Futebol", times_ext)
}

# ================= BOTÃO =================
class Botao(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texto):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 220))
        pygame.draw.rect(self.image, PRETO, self.image.get_rect(), 2)
        txt = fonte.render(texto, True, PRETO)
        self.image.blit(txt, (w//2 - txt.get_width()//2, h//2 - txt.get_height()//2))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.texto = texto

# ================= BOTÕES =================
btn_jogar = Botao(350, 260, 200, 55, "JOGAR")
btn_conquistas = Botao(350, 330, 200, 55, "CONQUISTAS")
btn_voltar = Botao(350, 450, 200, 50, "VOLTAR")

btn_estados = Botao(300, 220, 300, 50, "ESTADOS")
btn_paises = Botao(300, 290, 300, 50, "PAÍSES")
btn_times = Botao(300, 360, 300, 50, "TIMES")

# ================= CAIXA BRANCA ALINHADA =================
def desenhar_caixa_texto(texto, cor_texto, x, y, largura=360, altura=40):
    fundo = pygame.Surface((largura, altura), pygame.SRCALPHA)
    fundo.fill((255, 255, 255, 245))
    tela.blit(fundo, (x, y))

    pygame.draw.rect(tela, BRANCO, (x, y, largura, altura), 2)

    txt = fonte.render(texto, True, cor_texto)
    txt_rect = txt.get_rect(center=(x + largura // 2, y + altura // 2))
    tela.blit(txt, txt_rect)

# ================= FUNÇÕES =================
def atualizar_medalhas():
    global medalha_bronze, medalha_prata, medalha_ouro
    total = sum(len(perguntas[m]) for m in perguntas)
    medalha_bronze = acertos_totais >= 25
    medalha_prata = acertos_totais >= 50
    medalha_ouro = acertos_totais >= total

def tela_menu():
    tela.blit(fundo_menu, (0, 0))
    tela.blit(fonte_titulo.render("ADIVINHE A BANDEIRA", True, PRETO), (200, 120))
    tela.blit(btn_jogar.image, btn_jogar.rect)
    tela.blit(btn_conquistas.image, btn_conquistas.rect)

def tela_modos():
    tela.blit(fundo_menu, (0, 0))
    tela.blit(fonte_titulo.render("ESCOLHA O MODO", True, PRETO), (260, 120))
    tela.blit(btn_estados.image, btn_estados.rect)
    tela.blit(btn_paises.image, btn_paises.rect)
    tela.blit(btn_times.image, btn_times.rect)

def tela_conquistas():
    atualizar_medalhas()
    tela.blit(fundo_menu, (0, 0))
    tela.blit(fonte_titulo.render("CONQUISTAS", True, PRETO), (330, 120))

    x = 270
    desenhar_caixa_texto(
        f"Bronze (25 acertos): {'OK' if medalha_bronze else 'Bloqueada'}",
        BRONZE, x, 240
    )
    desenhar_caixa_texto(
        f"Prata (50 acertos): {'OK' if medalha_prata else 'Bloqueada'}",
        PRATA, x, 300
    )
    desenhar_caixa_texto(
        f"Ouro (Total): {'OK' if medalha_ouro else 'Bloqueada'}",
        OURO, x, 360
    )

    tela.blit(btn_voltar.image, btn_voltar.rect)

def carregar_pergunta():
    global botoes_opcoes
    botoes_opcoes = []
    dados = perguntas[modo][indice]
    for i, opcao in enumerate(dados["opcoes"]):
        botoes_opcoes.append(Botao(300, 360 + i*45, 300, 35, opcao))

def tela_quiz():
    tela.blit(fundo_quiz, (0, 0))
    dados = perguntas[modo][indice]
    tela.blit(dados["imagem"], (250, 80))
    for b in botoes_opcoes:
        tela.blit(b.image, b.rect)

    tempo = TEMPO_MAX - int(time.time() - inicio_tempo)
    tela.blit(fonte.render(f"Tempo: {tempo}s", True, BRANCO), (20, 20))

def tela_resultado():
    tela.blit(fundo_quiz, (0, 0))
    tela.blit(imagem_resultado, (250, 220))

# ================= LOOP =================
rodando = True
while rodando:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            rodando = False

        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = e.pos

            if estado == MENU:
                if btn_jogar.rect.collidepoint(pos):
                    estado = MODOS
                elif btn_conquistas.rect.collidepoint(pos):
                    estado = TELA_CONQUISTAS

            elif estado == MODOS:
                if btn_estados.rect.collidepoint(pos):
                    modo = "Estados"
                elif btn_paises.rect.collidepoint(pos):
                    modo = "Países"
                elif btn_times.rect.collidepoint(pos):
                    modo = "Times"

                if modo:
                    indice = 0
                    inicio_tempo = time.time()
                    carregar_pergunta()
                    estado = QUIZ

            elif estado == QUIZ:
                resposta = perguntas[modo][indice]["resposta"]
                for b in botoes_opcoes:
                    if b.rect.collidepoint(pos):
                        imagem_resultado = img_acerto if b.texto[0] == resposta else img_erro
                        if b.texto[0] == resposta:
                            acertos_totais += 1
                        estado = RESULTADO

            elif estado == RESULTADO:
                indice += 1
                if indice < len(perguntas[modo]):
                    inicio_tempo = time.time()
                    carregar_pergunta()
                    estado = QUIZ
                else:
                    estado = MENU
                    modo = ""

            elif estado == TELA_CONQUISTAS:
                if btn_voltar.rect.collidepoint(pos):
                    estado = MENU

    if estado == QUIZ and TEMPO_MAX - int(time.time() - inicio_tempo) <= 0:
        imagem_resultado = img_erro
        estado = RESULTADO

    if estado == MENU:
        tela_menu()
    elif estado == MODOS:
        tela_modos()
    elif estado == QUIZ:
        tela_quiz()
    elif estado == RESULTADO:
        tela_resultado()
    elif estado == TELA_CONQUISTAS:
        tela_conquistas()

    pygame.display.update()

pygame.quit()
sys.exit()
