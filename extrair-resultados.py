#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import glob
import ntpath as ospath
import datetime
import sys
import textwrap

RESULTADOS = '../Resultados/'

ORDEM = {}
i=0
for t in ["SNR", "CODEC", "CODEC4KHZ"]:
    ORDEM[t] = i
    i += 1
del i

def get_field(s):
    s = s.split(':', maxsplit=1)
    return s[1].strip()

class TSException(Exception): pass

class TSTrainamentoException(TSException): pass

class TS:
    def __init__(self, teste=None, ouvinte=None, fname=None, nota=None):
        if fname is None:
            return
        fname = ospath.basename(fname)
        fname = ospath.splitext(fname)[0]
        if fname.startswith('treinamento_'):
            raise TSTrainamentoException(
                "Testes de treinamento não devem ser salvos.")
        fname = fname.split('__')
        self.ouvinte = ouvinte
        self.nota = nota
        self.sinal = Sinal(fname[0], teste, fname[2])

class Sinal:
    def __init__(self, nome, teste, parametro):
        self.nome = nome
        self.teste = teste
        self.parametro = parametro
    def __eq__(self, other):
        return (self.nome==other.nome  and
                self.teste==other.teste  and
                self.parametro==other.parametro)

def get_datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

class Dados:

    sinais = [
        Sinal("Berimbau-vl",                "SNR",          "20dB"),
        Sinal("Berimbau-vl",                "SNR",          "35dB"),
        Sinal("Berimbau-vl",                "SNR",          "50dB"),

        Sinal("BluesInG_MJQ",               "SNR",          "20dB"),
        Sinal("BluesInG_MJQ",               "SNR",          "35dB"),
        Sinal("BluesInG_MJQ",               "SNR",          "50dB"),

        Sinal("Dubal",                      "SNR",          "20dB"),
        Sinal("Dubal",                      "SNR",          "35dB"),
        Sinal("Dubal",                      "SNR",          "50dB"),

        Sinal("HaGenteAqui-MJ",             "SNR",          "20dB"),
        Sinal("HaGenteAqui-MJ",             "SNR",          "35dB"),
        Sinal("HaGenteAqui-MJ",             "SNR",          "50dB"),

        Sinal("Largo_Schulz-hv",            "SNR",          "20dB"),
        Sinal("Largo_Schulz-hv",            "SNR",          "35dB"),
        Sinal("Largo_Schulz-hv",            "SNR",          "50dB"),

        Sinal("Royer-cravo",                "SNR",          "20dB"),
        Sinal("Royer-cravo",                "SNR",          "35dB"),
        Sinal("Royer-cravo",                "SNR",          "50dB"),

        #Sinal("Valsa_Chopin-Godowsky_1916", "SNR",          "20dB"),
        #Sinal("Valsa_Chopin-Godowsky_1916", "SNR",          "35dB"),
        #Sinal("Valsa_Chopin-Godowsky_1916", "SNR",          "50dB"),


        Sinal("Berimbau-vl",                "CODEC",        "64k"),
        #Sinal("Berimbau-vl",                "CODEC",        "128k"),
        Sinal("Berimbau-vl",                "CODEC",        "320k"),

        Sinal("BluesInG_MJQ",               "CODEC",        "64k"),
        Sinal("BluesInG_MJQ",               "CODEC",        "128k"),
        Sinal("BluesInG_MJQ",               "CODEC",        "320k"),

        Sinal("Dubal",                      "CODEC",        "64k"),
        Sinal("Dubal",                      "CODEC",        "128k"),
        Sinal("Dubal",                      "CODEC",        "320k"),

        Sinal("HaGenteAqui-MJ",             "CODEC",        "64k"),
        Sinal("HaGenteAqui-MJ",             "CODEC",        "128k"),
        Sinal("HaGenteAqui-MJ",             "CODEC",        "320k"),

        Sinal("Largo_Schulz-hv",            "CODEC",        "64k"),
        Sinal("Largo_Schulz-hv",            "CODEC",        "128k"),
        Sinal("Largo_Schulz-hv",            "CODEC",        "320k"),

        Sinal("Royer-cravo",                "CODEC",        "64k"),
        Sinal("Royer-cravo",                "CODEC",        "128k"),
        Sinal("Royer-cravo",                "CODEC",        "320k"),

        Sinal("Valsa_Chopin-Godowsky_1916", "CODEC",        "64k"),
        #Sinal("Valsa_Chopin-Godowsky_1916", "CODEC",        "128k"),
        Sinal("Valsa_Chopin-Godowsky_1916", "CODEC",        "320k"),


        Sinal("Berimbau-vl",                "CODEC4KHZ",    "64k"),

        Sinal("BluesInG_MJQ",               "CODEC4KHZ",    "64k"),

        Sinal("Dubal",                      "CODEC4KHZ",    "64k"),

        Sinal("HaGenteAqui-MJ",             "CODEC4KHZ",    "64k"),

        Sinal("Largo_Schulz-hv",            "CODEC4KHZ",    "64k"),

        Sinal("Royer-cravo",                "CODEC4KHZ",    "64k"),

        Sinal("Valsa_Chopin-Godowsky_1916", "CODEC4KHZ",    "64k"),
    ]

    def __init__(self):
        self.nomes = []
        self.notas = {}
        self.tempos = {}

    def add_sessão(self, fname):
        with open(fname, 'r', encoding="ISO-8859-1") as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines if len(l.strip())>0]
        teste = lines.pop(0)
        ouvinte = get_field(lines.pop(0))
        primeira_sessão = not(ouvinte in self.nomes)
        if primeira_sessão:
            self.nomes.append(ouvinte)
        lines.pop(0) # supervisor
        starttime = get_datetime(get_field(lines.pop(0)))
        endtime = get_datetime(get_field(lines.pop(0)))
        duração = endtime - starttime
        if primeira_sessão:
            if ouvinte in self.tempos:
                raise TSException("Erro! O nome ‘{}’ não existe na lista"
                    " de nomes, mas existe na lista de tempos.")
            if ouvinte in self.notas:
                raise TSException("Erro! O nome ‘{}’ não existe na lista"
                    " de nomes, mas existe na matriz de notas.")
            self.tempos[ouvinte] = [None, None, None]
            self.notas[ouvinte] = [-100 for s in self.sinais]
        if self.tempos[ouvinte][ORDEM[teste]] is not None:
            raise TSException("Erro! ‘{}’ fez duas vezes o teste ‘{}’".format(
                ouvinte, teste))
        self.tempos[ouvinte][ORDEM[teste]] = duração # .total_seconds()
        while len(lines) > 0:
            lines.pop(0) # referência
            fname = lines.pop(0)
            nota = int(lines.pop(0))
            try:
                ts = TS(teste, ouvinte, fname, nota)
            except TSTrainamentoException:
                continue
            if self.notas[ouvinte][self.sinais.index(ts.sinal)] >= 0:
                tw = textwrap.TextWrapper(subsequent_indent='WARNING:         ',
                                          initial_indent='WARNING: ',
                                          replace_whitespace=False, width=100)
                msg = ("‘{}’ fez duas vezes o teste ‘{} / {} / {}’.\n"
                       "As notas foram, respectivamente {} e {}.\n"
                       "A segunda nota foi descartada.").format(
                           ts.ouvinte, ts.sinal.teste, ts.sinal.nome,
                           ts.sinal.parametro,
                           self.notas[ouvinte][self.sinais.index(ts.sinal)],
                           ts.nota
                      ).splitlines()
                for l in msg:
                    print(tw.fill(l), file=sys.stderr)
                print(file=sys.stderr)
            self.notas[ouvinte][self.sinais.index(ts.sinal)] = ts.nota

    def dump(self):
        s  = ""
        s += "% Resultados dos testes subjetivos\n"
        s += "% Arquivo gerado às: " + str(datetime.datetime.now()) + "\n"
        s += "%\n"
        s += "\n"
        s += "NOMES = {\n"
        for n in self.nomes:
            s += "    '{}'\n".format(n)
        s += "};\n"
        s += "\n"
        s += "NOTAS = [\n"
        for n in self.nomes:
            s += "    "
            for sinal in self.sinais:
                nota = self.notas[n][self.sinais.index(sinal)]
                if nota < 0:
                    nota = "Inf"
                s += "{}, ".format(nota)
            s += "\n"
        s += "];\n"
        s += "\n"
        s += "TEMPOS = [\n"
        for n in self.nomes:
            s += "    "
            for t in self.tempos[n]:
                try:
                    s += "{}, ".format(t.total_seconds()/60)
                except AttributeError:
                    s += "NaN, "
            s += "\n"
        s += "];\n"
        s += "\n"
        s += "SINAIS = [\n"
        for sinal in self.sinais:
            s += "    struct("
            s += "'sinal', '{}', ".format(sinal.nome)
            s += "'teste', '{}', ".format(sinal.teste)
            s += "'parametro', '{}'".format(sinal.parametro)
            s += ")\n"
        s += "];\n"
        return s

if __name__ == '__main__':

    sessões = [f for f in glob.glob(RESULTADOS + '/*/*') if not f.endswith('~')]

    dados = Dados()

    for s in sessões:
        dados.add_sessão(s)
        dados.nomes.sort()

    print(dados.dump())
