from __future__ import division
import pygame
import sys
import pygame.mixer
import math
import matplotlib
import numpy as np
import time
import random
import matplotlib.pyplot as plt
from pygame.locals import *


pygame.init()


pygame.display.set_caption('Entropia') # tytul okna
czas = pygame.time.Clock() # obiekt do sledzenia czasu
X, Y = 0, 0
szerokosc, wysokosc = 600, 600 # wielkosc pola zderzen
x, y = szerokosc / 2, wysokosc / 2 # wielkosc pola zderzen malego
rozmiar = 620, 800 # wielkosc okna
ekran = pygame.display.set_mode(rozmiar) # inicjuje wyswietlacz
czcionka = pygame.font.SysFont("times", 41)

centerX, centerY = int(x), int(y) # potrzebne do predkosci ? a nie do pozycji?? przestrzen predkosci??
start = time.time()
ostatni = 0 # ???
vmax = 5
promien = 3
atomy = 200
delta_t = atomy / 80 # krok czasu, przyrost? 80 wynika z zadania z ograniczenia tej przestrzeni predkosci W(vmax)
przed = 0 # do glownej petli
po = 0 # do glownej petli

polozenie = []
v = []
kolor = []
wyniki = []  # wykres (entropia)
czas_y = []  # czas na wykresie (oú y)

czas_wykresu = 10
rozmiar_wykresu = 100


# poczatkowe pozycje i predkosci i kolory
for j in range(atomy):
    polozenie.append([random.randint(0, centerX), random.randint(0, centerY), 0])
    v.append([random.uniform(-vmax, vmax), random.uniform(-vmax, vmax)])
    kolor.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))


def zlicz(N):
    tab = []
    for i in range(16):
        tab.append(0)
    for i in range(N):
        if polozenie[i][0] < centerX:
            x = 0
        else:
            x = 1
        if polozenie[i][1] < centerY:
            y = 0
        else:
            y = 1
        if v[i][0] < 0:
            vx = 0
        else:
            vx = 1
        if v[i][1] < 0:
            vy = 0
        else:
            vy = 1

        stan = [x, y, vx, vy]
        j = 1
        suma1 = 0
        for n in stan[::-1]:
            suma1 += n * j
            j *= 2
        tab[suma1] += 1
    return tab


def entropia(N):
    tab = zlicz(N)
    suma2 = 0
    for i in range(16):  # mamy 16 makrostanow, bo okreslone jako 0 i 1, 4 wartosci, czyli 2^4
        if tab[i] > 0:
            suma2 += tab[i] * math.log(tab[i])
    return N * math.log(N) - suma2


plt.style.use('ggplot')


# a - list of all atoms, v - list of all velocites (atom j is in position position[j] and travel with velocity v[j]), b - the atom we check for collisions
def kolizja(l, v, k):
    for kulka in l:
        if kulka is not k:
            odlegloscX, odlegloscY = (k[0] - kulka[0]), (k[1] - kulka[1])
            odleglosc = math.sqrt(odlegloscX ** 2 + odlegloscY ** 2)
            if odleglosc < (2 * promien) + promien / 100: # nie wiem, czy to dobrze, z polecenia
                i, j = l.index(kulka), l.index(k)
                zmiana = [-0.15 * odlegloscX, -0.15 * odlegloscY]
                Vlx, Vly = v[i][0], v[i][1]
                Vkx, Vky = v[j][0], v[j][1]
                kat = math.atan2(odlegloscY, odlegloscX)  # math.acos((distanceX/distance))
                cos, sin = math.cos(kat), math.sin(kat)
                # ze wzorow:
                [Vlg, Vlh], [Vkg, Vkh] = [Vlx * cos + Vly * sin, Vly * cos - Vlx * sin], [Vkx * cos + Vky * sin,
                                                                                          Vky * cos - Vkx * sin]
                sin = -sin
                v1, v2 = [Vkg * cos + Vlh * sin, Vlh * cos - Vkg * sin], [Vlg * cos + Vkh * sin, Vkh * cos - Vlg * sin]
                v[i], v[j] = v2, v1  # nowe predkosci
                l[i][0], l[i][1] = l[i][0] + zmiana[0], l[i][1] + zmiana[1]  # treating overlaps
    return ()


# wszystko w ruch
while 1:
    ekran.fill((0, 0, 0))
    pygame.draw.rect(ekran, (0, 0, 255), (X, Y, szerokosc, wysokosc), 3)
    pygame.draw.rect(ekran, (54, 123, 160), (110, 610, 380, 170), 4)

    for wyjscie in pygame.event.get():
        if wyjscie.type == pygame.QUIT:
            sys.exit()

    czas_trwania = time.time() - start - po + przed
    czas_trwania_z=round(czas_trwania, 2)
    # poczatek
    if czas_trwania < 5:
        scianaX, scianaY = szerokosc / 2, wysokosc / 2
        pygame.draw.line(ekran, (0, 0, 255), (centerY, 0), (centerX, centerY), 3)
        pygame.draw.line(ekran, (0, 0, 255), (0, centerX), (centerX, centerY), 3)
    else:
        scianaX, scianaY = szerokosc, wysokosc


    # sprawdzanie kolizji z kulkami innymi i ze scianami
    for j in range(len(polozenie[:atomy])):
        kolizja(polozenie, v, polozenie[j])
        polozenie[j][0] += v[j][0]
        polozenie[j][1] += v[j][1]


        if polozenie[j][0] + promien > X + scianaX:
            v[j][0] = -1 * (v[j][0])
            polozenie[j] = [(-promien + X + scianaX) - 2, polozenie[j][1], 0]

        if polozenie[j][0] - promien < X:
            v[j][0] = -1 * (v[j][0])
            polozenie[j] = [promien + X + 2, polozenie[j][1], 0]

        if polozenie[j][1] + promien > Y + scianaY:
            v[j][1] = -1 * (v[j][1])
            polozenie[j] = [polozenie[j][0], (-promien + Y + scianaY) - 2, 0]

        if polozenie[j][1] - promien < Y:
            v[j][1] = -1 * (v[j][1])
            polozenie[j] = [polozenie[j][0], Y + 2 + promien, 0]

    # o co chodzi z tym kolkiem???
    czas.tick(60)
    for i in range(len(polozenie[:atomy])):
        circle = pygame.draw.circle(ekran, kolor[i], (int(polozenie[i][0]), int(polozenie[i][1])), promien)

    en = round(entropia(atomy),4)
    tekst_render = czcionka.render(str(en), 1, (255, 0, 0))
    ekran.blit(czcionka.render("Entropia:", 1, (250, 250, 250)), (150, 630))
    ekran.blit(tekst_render, (330, 630))
    ekran.blit(czcionka.render("Czas:", 1, (250, 250, 250)), (150, 700))
    ekran.blit(czcionka.render(str(czas_trwania_z), 1, (250, 0, 0)), (330, 700))


    # wykres
    if czas_trwania - ostatni > delta_t:
        ostatni += delta_t
        wyniki.append(en)
        czas_y.append(czas_trwania)

    if czas_trwania > czas_wykresu:
        plt.plot(czas_y, wyniki)
        przed += time.time()
        plt.show()
        po += time.time()
        czas_wykresu += 10


    pygame.display.flip()