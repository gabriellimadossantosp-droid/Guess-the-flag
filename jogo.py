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

# ================= FONTES =================
fonte = pygame.font.SysFont("arial", 24)
fonte_titulo = pygame.font.SysFont("arial", 40)

# ================= ESTADOS DO JOGO =================
MENU = 0
MODOS = 1
QUIZ = 2
RESULTADO = 3
TELA_CONQUISTAS = 4
estado = MENU

#CONQUISTAS
acertos_totais = 0

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

# ================= PEGAR SIGLAS DAS PASTAS =================
def pegar_siglas_da_pasta(pasta):
    siglas = []
    extensoes = []
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            sigla = os.path.splitext(arquivo)[0]
            extensao = os.path.splitext(arquivo)[1]
            siglas.append(sigla)
            extensoes.append(extensao)
    return siglas, extensoes

estados_siglas, estados_extensoes = pegar_siglas_da_pasta("Estados Brasileiros")
paises_siglas, paises_extensoes = pegar_siglas_da_pasta("Países")
times_siglas, times_extensoes = pegar_siglas_da_pasta("Times de Futebol")

# ================= GERADOR DE PERGUNTAS =================
def gerar_perguntas(lista_siglas, pasta, lista_extensoes):
    perguntas = []

    for i, sigla in enumerate(lista_siglas):
        #imagem = carregar_imagem(f"{pasta}/{sigla}.png", (400, 250))
        imagem = carregar_imagem(f"{pasta}/{sigla}{lista_extensoes[i]}", (400, 250))

        opcoes = random.sample(lista_siglas, min(4, len(lista_siglas)))
        if sigla not in opcoes:
            opcoes[0] = sigla
        random.shuffle(opcoes)

        letras = ["A", "B", "C", "D"]
        opcoes_formatadas = [
            f"{letras[i]} - {opcoes[i]}" for i in range(len(opcoes))
        ]

        resposta = letras[opcoes.index(sigla)]

        perguntas.append({
            "imagem": imagem,
            "opcoes": opcoes_formatadas,
            "resposta": resposta
        })

    random.shuffle(perguntas)
    return perguntas

# ================= PERGUNTAS =================
perguntas = {
    "Estados": gerar_perguntas(estados_siglas, "Estados Brasileiros", estados_extensoes),
    "Países": gerar_perguntas(paises_siglas, "Países", paises_extensoes),
    "Times": gerar_perguntas(times_siglas, "Times de Futebol", times_extensoes)
}

# ================= CLASSE BOTÃO =================
class Botao(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texto):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 220))
        pygame.draw.rect(self.image, PRETO, self.image.get_rect(), 2)

        txt = fonte.render(texto, True, PRETO)
        self.image.blit(
            txt,
            (w // 2 - txt.get_width() // 2,
             h // 2 - txt.get_height() // 2)
        )

        self.rect = self.image.get_rect(topleft=(x, y))
        self.texto = texto

# ================= GRUPOS =================
botoes_menu = pygame.sprite.Group()
botoes_modos = pygame.sprite.Group()
botoes_opcoes = pygame.sprite.Group()

# ================= BOTÕES =================
btn_jogar = Botao(350, 260, 200, 55, "JOGAR")
btn_conquistas = Botao(350, 330, 200, 55, "CONQUISTAS")
botoes_menu.add(btn_jogar, btn_conquistas)

btn_estados = Botao(300, 220, 300, 50, "ESTADOS")
btn_paises = Botao(300, 290, 300, 50, "PAÍSES")
btn_times = Botao(300, 360, 300, 50, "TIMES")

botoes_modos.add(btn_estados, btn_paises, btn_times)

# ================= FUNÇÕES =================
def carregar_pergunta():
    botoes_opcoes.empty()
    dados = perguntas[modo][indice]
    for i, opcao in enumerate(dados["opcoes"]):
        botoes_opcoes.add(Botao(300, 360 + i * 45, 300, 35, opcao))

def tela_menu():
    tela.blit(fundo_menu, (0, 0))
    titulo = fonte_titulo.render("ADIVINHE A BANDEIRA", True, PRETO)
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 120))
    botoes_menu.draw(tela)

def tela_modos():
    tela.blit(fundo_menu, (0, 0))
    titulo = fonte_titulo.render("ESCOLHA O MODO", True, PRETO)
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 120))
    botoes_modos.draw(tela)

def tela_quiz():
    tela.blit(fundo_quiz, (0, 0))
    dados = perguntas[modo][indice]
    tela.blit(dados["imagem"], (250, 80))
    botoes_opcoes.draw(tela)

    tempo = TEMPO_MAX - int(time.time() - inicio_tempo)
    tela.blit(fonte.render(f"Tempo: {tempo}s", True, BRANCO), (20, 20))

def tela_resultado():
    tela.blit(fundo_quiz, (0, 0))
    tela.blit(
        imagem_resultado,
        (LARGURA//2 - imagem_resultado.get_width()//2, 220)
    )

# ================= LOOP PRINCIPAL =================
rodando = True
while rodando:
    clock.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = evento.pos

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
                for botao in botoes_opcoes:
                    if botao.rect.collidepoint(pos):
                        letra = botao.texto[0]

                        if letra == resposta:
                            imagem_resultado = img_acerto
                            acertos_totais += 1

                        else:
                            imagem_resultado = img_erro
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

    pygame.display.update()

pygame.quit()
sys.exit()
