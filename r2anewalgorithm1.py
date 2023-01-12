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


class R2ANewAlgorithm1(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = [] #lista com as taxas de transmissao de bits
        self.request_time = 0 #tempo de uma requisicao
        self.qi = [] #lista com as opcoes de qualidade

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload()) #testeblabla
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.request_time = time.perf_counter()
        if not self.throughputs: #se o algoritmo acabou de comecar, entao a qualidade escolhida sera a pior
            qualidade = self.qi[0]
        else: #senao
            media = mean(self.throughputs)  # media das taxas
            mad_weighted = 0 #media do desvio absoluto com pesos (pesquise apenas mad no google).mad mostra se a estabilidade da rede

            for indice, item in enumerate(self.throughputs):
                mad_weighted += (indice + 1) * abs(item - media) #o vetor ja esta ordenado do dado mais antigo para o dado mais recente
                #colocamos um peso nos itens da taxa para que os mais recentes tenham peso maior
            mad_weighted = (mad_weighted)/len(self.throughputs)
            probabilidade = (media)/(media + mad_weighted) #tendencia de mudar de qualidade

            i = 0
            while qualidade != self.qi[i]:
                i +=1

            aumentar = probabilidade*(self.qi[min(len(self.qi), i+1)]) #tendencia de aumentar a qualidade
            diminuir = (1-probabilidade)*(self.qi[max(0, i-1)]) #tendencia de diminuir a qualidade

            qualidade = argmin(qualidade - diminuir + aumentar)

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

