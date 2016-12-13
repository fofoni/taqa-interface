#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt4 import QtGui, QtCore, phonon


MSGS = {'CODEC': '',  'SNR': ''}

MSGS['CODEC']  = "Escute o sinal original e o sinal degradado. O quão diferente"
MSGS['CODEC'] += " o degradado é do original?"

MSGS['SNR']    = "Escute o sinal original e o sinal degradado. O quão pior é o"
MSGS['SNR']   += " degradado em relação ao original?"


class FileSelectWidget(QtGui.QWidget):
    def __init__(self, parent=None, parentWindow=None):
        super().__init__(parent)
        self.pWin = parentWindow
        layout = QtGui.QHBoxLayout(self)
        self.file_path_edit = QtGui.QLineEdit(self)
        self.file_path_edit.setPlaceholderText(
            "Selecione uma sequência de testes.")
        layout.addWidget(self.file_path_edit)
        self.choose_button = QtGui.QPushButton(self)
        self.choose_button.setText("&Abrir arquivo")
        self.choose_button.setIcon(QtGui.QIcon.fromTheme("document-open"))
        layout.addWidget(self.choose_button)
        self.file_path_edit.returnPressed.connect(self.returnPressed)
        self.file_path_edit.textChanged.connect(self.textChanged)
        self.choose_button.clicked.connect(self.showDialog)
        self.setLayout(layout)
    def text(self):
        return self.file_path_edit.text()
    returnPressed = QtCore.pyqtSignal()
    textChanged = QtCore.pyqtSignal(str)
    def showDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(
            self.pWin, 'Selecione arquivo de sequência', os.getcwd(),
            "Sequência de testes (*.txt)")
        if not fname=="":
            self.file_path_edit.setText(fname)
    def setDisabled(self):
        self.file_path_edit.setDisabled(True)
        self.choose_button.setDisabled(True)


def play_file(fname):
    output = phonon.Phonon.AudioOutput(phonon.Phonon.MusicCategory)
    m_media = phonon.Phonon.MediaObject()
    phonon.Phonon.createPath(m_media, output)
    m_media.setCurrentSource(phonon.Phonon.MediaSource(fname))
    m_media.play()


class ComparaçãoDialog(QtGui.QDialog):
    playbtn_height = 42
    def __init__(self, parent, índice, tipo, arquivos):
        super().__init__(parent)
        self.arquivos = arquivos
        layout = QtGui.QVBoxLayout()
        self.enunciado = QtGui.QLabel(
            "<b>{})</b> ".format(índice) + MSGS[tipo],
            self)
        layout.addWidget(self.enunciado)
        play_buttons = QtGui.QHBoxLayout()
        self.orig_button = QtGui.QPushButton(self)
        self.orig_button.setText("Original")
        self.orig_button.setMinimumHeight(self.playbtn_height)
        self.orig_button.setCheckable(True)
        self.orig_button.clicked.connect(self.click_orig)
        play_buttons.addWidget(self.orig_button)
        self.deg_button = QtGui.QPushButton(self)
        self.deg_button.setText("Degradado")
        self.deg_button.setMinimumHeight(self.playbtn_height)
        self.deg_button.setCheckable(True)
        self.deg_button.clicked.connect(self.click_deg)
        play_buttons.addWidget(self.deg_button)
        layout.addLayout(play_buttons)
        self.setLayout(layout)
    def click_orig(self, checked):
        if checked:
            if self.deg_button.isChecked():
                #TODO: pausar musica do deg
                self.deg_button.setChecked(False)
            play_file(self.arquivos[0])
        else:
            #TODO: pausar musica
            pass
    def click_deg(self, checked):
        if checked:
            if self.orig_button.isChecked():
                #TODO: pausar musica do orig
                self.orig_button.setChecked(False)
            #TODO: tocar musica
        else:
            #TODO: pausar musica
            pass

# Janela para iniciar uma sessão de Testes Subjetivos
class SessãoTS(QtGui.QWidget):

    def __init__(self, *args):

        super().__init__(*args)

        self.setWindowTitle('Sessão de Testes Subjetivos')

        vbox = QtGui.QVBoxLayout(self)

        self.file_seq = FileSelectWidget(parent=self, parentWindow=self)
        vbox.addWidget(self.file_seq)

        fbox = QtGui.QFormLayout()
        self.label_tester = QtGui.QLabel("Nome do testador:", self)
        self.line_tester = QtGui.QLineEdit(self)
        fbox.addRow(self.label_tester, self.line_tester)
        self.label_super = QtGui.QLabel("Nome do supervisor:", self)
        self.line_super = QtGui.QLineEdit(self)
        fbox.addRow(self.label_super, self.line_super)
        vbox.addLayout(fbox)

        hbox = QtGui.QHBoxLayout()
        self.begin_button = QtGui.QPushButton(self)
        self.begin_button.setText("&Começar!")
        self.begin_button.setDisabled(True)
        hbox.addWidget(self.begin_button)
        self.save_button = QtGui.QPushButton(self)
        self.save_button.setText("Salvar resultado")
        self.save_button.setDisabled(True)
        hbox.addWidget(self.save_button)
        vbox.addLayout(hbox)

        self.begin_button.clicked.connect(self.file_seq.setDisabled)
        self.file_seq.textChanged.connect(self.valida_campos)
        self.line_tester.textChanged.connect(self.valida_campos)
        self.line_super.textChanged.connect(self.valida_campos)
        self.begin_button.clicked.connect(self.begin_sess)

        self.setLayout(vbox)

    def valida_campos(self):
        if self.file_seq.text()=="":
            self.begin_button.setDisabled(True)
        elif self.line_tester.text()=="":
            self.begin_button.setDisabled(True)
        elif self.line_super.text()=="":
            self.begin_button.setDisabled(True)
        else:
            self.begin_button.setDisabled(False)

    def begin_sess(self):
        self.file_seq.setDisabled()
        with open(self.file_seq.text()) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines if l.strip()!=""]
        self.tipo = lines.pop(0)
        i=0
        self.testes = []
        for i in range(len(lines)//2):
            self.testes.append((lines[2*i], lines[2*i+1]))
        comparação = ComparaçãoDialog(self, 'coé', self.tipo, self.testes[0])
        comparação.exec()


def main():

    app = QtGui.QApplication(sys.argv)

    w = SessãoTS()
    w.setFocus()
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
