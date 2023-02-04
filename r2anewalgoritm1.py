"""
Autores:
    Matheus Guaraci 180046951
    Leonardo Maximo
    Gabriel Nascimento
"""

from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean
from numpy import argmin


class R2ANewAlgoritm1(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = [] #lista com as taxas de transmissao de bits
        self.request_time = 0 #tempo de uma requisicao
        self.qi = [] #lista com as opcoes de qualidade
        self.indice = 0 #indice da qualidade anterior

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi() #monta a lista de qualidades

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.request_time = time.perf_counter()
        #print("Índice: ", self.indice)
        if self.throughputs == []: #se o algoritmo acabou de comecar, entao a qualidade escolhida sera a pior
            qualidade = self.qi[0]
            self.indice = 0
        else: #senao
            qualidade = self.qi[self.indice] #coloca a qualidade anterior na variavel
            media = mean(self.throughputs)
            mad_weighted = 0 #media do desvio absoluto com pesos (pesquise apenas mad no google).mad mostra se a estabilidade da rede
            for indice, item in enumerate(self.throughputs):
                soma = item - media #calcula o valor do item menos a media
                soma = abs(soma) #tira qualquer sinal dessa soma para que fique sempre positivo
                mad_weighted += ((indice + 1)/len(self.throughputs)) * soma  #calcula a mad
                # colocamos um peso nos itens da taxa para que os mais recentes tenham peso maior

            probabilidade = (media)/(media + mad_weighted) #tendencia de mudar de qualidade
            aumentar = probabilidade*(self.qi[min(len(self.qi)-1, self.indice+1)]) #tendencia de aumentar a qualidade
            diminuir = (1-probabilidade)*(self.qi[max(0, self.indice-1)]) #tendencia de diminuir a qualidade
            print("Qualidade Real: " , qualidade)
            qualidadeAux = qualidade - diminuir + aumentar #calcula o valor da proxima qualidade
            print("Média: " , media)
            print("DesvPad: " , mad_weighted)
            print("Probabilidade: " , probabilidade)
            print("aumentar: " , aumentar)
            print("Diminuir: " , diminuir)
            print("QualidadeAux: " , qualidadeAux)
            #print(self.throughputs)
            print(self.qi)
            for indice, item in enumerate(self.qi):
                if qualidadeAux <= item:
                    self.indice = indice #salva o indice atual, pois o atual vira o anterior da proxima chamada do handle
                    qualidade = item
                    break
            print("Qualidade que ira pedir: ", qualidade)

        msg.add_quality_id(qualidade)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass