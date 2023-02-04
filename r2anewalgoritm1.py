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
        self.n = 10 #Tamanho da Janela de Throughputs determinada experimentalmente

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
        n = self.n
        #print("Índice: ", self.indice)
        if self.throughputs == []: #se o algoritmo acabou de comecar, entao a qualidade escolhida sera a pior
            qualidade = self.qi[0]
            self.indice = 0
        else: #senao
            qualidade = self.qi[self.indice] #coloca a qualidade anterior na variavel
            media = 0
            if(len(self.throughputs) < n):
                media = mean(self.throughputs)
            else:
                for i in range(n):
                    media += self.throughputs[len(self.throughputs)-1-i]/n  # media das taxas
            mad_weighted = 0 #media do desvio absoluto com pesos (pesquise apenas mad no google).mad mostra se a estabilidade da rede
            if(len(self.throughputs) >= n):
                for i in range(10):
                    mad_weighted += ((n - i)/(n))*(abs(self.throughputs[len(self.throughputs)-1-i] - media)) #o vetor ja esta ordenado do dado mais antigo para o dado mais recente
                #colocamos um peso nos itens da taxa para que os mais recentes tenham peso maior
            #mad_weighted = (mad_weighted)/len(self.throughputs)
            else:
                ind = 0
                for item in self.throughputs:
                    mad_weighted += ((ind + 1)/(len(self.throughputs)))*(abs(item - media)) #o vetor ja esta ordenado do dado mais antigo para o dado mais recente
                    ind+=1
            probabilidade = (media)/(media + mad_weighted) #tendencia de mudar de qualidade
            aumentar = probabilidade*(self.qi[min(len(self.qi), self.indice)]) #tendencia de aumentar a qualidade
            diminuir = (1-probabilidade)*(self.qi[max(0, self.indice-1)]) #tendencia de diminuir a qualidade
            print("Qualidade Real: " , qualidade)
            qualidadeAux = qualidade - diminuir + aumentar #atualiza o valor da qualidade
            print("Média: " , media)
            print("DesvPad: " , mad_weighted)
            #print("Probabilidade: " , probabilidade)
            print("aumentar: " , aumentar)
            print("Diminuir: " , diminuir)
            print("Qualidade: " , qualidadeAux)
            #print(self.throughputs)
            print(self.qi)
            aux = 0
            for item in self.qi:
                #print("Qualidade atual",item)
                #print("Indice", aux)
                if qualidadeAux > item:
                    #print("Qualidade posível",item)
                    qualidade = item
                    if aux < (len(self.qi)-1):
                        aux+=1

            self.indice = aux #salva o indice atual, pois o atual vira o anterior da proxima chamada do handle
        
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


