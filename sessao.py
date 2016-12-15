#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt4 import QtGui, QtCore
import wave, pyaudio
import time, threading


NEXT_TEST_CODE = 10001
PREV_TEST_CODE = 10000




"""
TODO:
1. aumentar                                              OK 20:00
2. nao deixar trocar no meio da musica
3. clicar na barrinha
4. CODEC-TELEFONE
5. Colocar horário de início e de fim no resultado
6. upsample nos 4khz
7. gerar sinais de treinamento
8. Equalizar potencia
"""




MSGS = {'CODEC': '',  'SNR': ''}
SLIDE_LEFT = MSGS.copy()
SLIDE_RIGHT = MSGS.copy()

MSGS['CODEC'] += "Escute os dois sinais a seguir. Avalie a diferença"
MSGS['CODEC'] += " do MODIFICADO em relação ao ORIGINAL"
SLIDE_LEFT['CODEC'] += "Diferença Mínima"
SLIDE_RIGHT['CODEC'] += "Diferença Máxima"

MSGS['SNR']   += "Escute os dois sinais a seguir. Avalie o grau de"
MSGS['SNR']   += " degradação do MODIFICADO em relação ao ORIGINAL."
SLIDE_LEFT['SNR'] += "Degradação Mínima"
SLIDE_RIGHT['SNR'] += "Degradação Máxima"

FAIXA_NOTAS = [0, 100]


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
    def setEnabled(self):
        self.file_path_edit.setDisabled(False)
        self.choose_button.setDisabled(False)


class ComparaçãoDialog(QtGui.QDialog):
    playbtn_height = 400
    sleep_resolution = 0.03
    def __init__(self, parent, índice, tipo, arquivos, noprev=False, nota=None):
        super().__init__(parent)
        self.arquivos = arquivos[0:2]
        self.listenedto = [False for i in range(2)]
        self.givenup = False
        layout = QtGui.QVBoxLayout()
        self.enunciado = QtGui.QLabel(""
            "<b>{})</b> ".format(índice) + MSGS[tipo],
            self)
        playbut_ss = """QPushButton {
            font-size: 28pt;
            font-weight: bold;
        }"""
        layout.addWidget(self.enunciado)
        play_buttons_hbox = QtGui.QHBoxLayout()
        self.play_buttons = [QtGui.QPushButton(self) for i in range(2)]
        self.play_buttons[0].setText("ORIGINAL")
        self.play_buttons[0].setMinimumHeight(self.playbtn_height)
        self.play_buttons[0].setCheckable(True)
        self.play_buttons[0].clicked.connect(self.click_orig)
        self.play_buttons[0].setStyleSheet(playbut_ss)
        play_buttons_hbox.addWidget(self.play_buttons[0])
        self.play_buttons[1].setText("MODIFICADO")
        self.play_buttons[1].setMinimumHeight(self.playbtn_height)
        self.play_buttons[1].setCheckable(True)
        self.play_buttons[1].clicked.connect(self.click_deg)
        self.play_buttons[1].setStyleSheet(playbut_ss)
        play_buttons_hbox.addWidget(self.play_buttons[1])
        layout.addLayout(play_buttons_hbox)
        slider_hbox = QtGui.QHBoxLayout()
        self.slidel_label = QtGui.QLabel(SLIDE_LEFT[tipo], self)
        slider_hbox.addWidget(self.slidel_label)
        self.slide = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slide.setMinimum(FAIXA_NOTAS[0])
        self.slide.setMaximum(FAIXA_NOTAS[1])
        slider_hbox.addWidget(self.slide)
        self.slider_label = QtGui.QLabel(SLIDE_RIGHT[tipo], self)
        if nota is None:
            self.slide.setDisabled(True)
            self.slidel_label.setDisabled(True)
            self.slider_label.setDisabled(True)
        else:
            self.slide.setValue(nota)
        slider_hbox.addWidget(self.slider_label)
        layout.addLayout(slider_hbox)
        butbox = QtGui.QHBoxLayout()
        self.prev_but = QtGui.QPushButton(self)
        self.prev_but.setText("<< Anterior")
        self.prev_but.setMaximumWidth(300)
        self.prev_but.clicked.connect(lambda: self.done(PREV_TEST_CODE))
        if noprev:
            self.prev_but.setDisabled(True)
        butbox.addWidget(self.prev_but)
        self.next_but = QtGui.QPushButton(self)
        self.next_but.setText("Próximo >>")
        self.next_but.setMaximumWidth(300)
        self.next_but.clicked.connect(lambda: self.done(NEXT_TEST_CODE))
        if nota is None:
            self.next_but.setDisabled(True)
        self.slide.sliderReleased.connect(
            lambda: self.next_but.setDisabled(False))
        self.slide.valueChanged.connect(
            lambda: self.next_but.setDisabled(False))
        butbox.addWidget(self.next_but)
        layout.addLayout(butbox)
        self.setLayout(layout)
        self.setMinimumWidth(1500)
        self.setMinimumHeight(800)
    def click_playbtn(self, checked, i):
        j = 1 if i==0 else 0
        self.play_buttons[0].setDisabled(True)
        self.play_buttons[1].setDisabled(True)
        if checked:
            if self.play_buttons[j].isChecked():
                self.givenup = True
                self.stop(j)
                self.play_buttons[j].setChecked(False)
            self.play_buttons[j].setDisabled(True)
            self.givenup = False
            self.play(i)
        else:
            self.givenup = True
            self.stop(i)
            self.play_buttons[j].setDisabled(False)
        self.play_buttons[i].setDisabled(False)
    click_orig = lambda self, checked: self.click_playbtn(checked, 0)
    click_deg  = lambda self, checked: self.click_playbtn(checked, 1)
    def __enter__(self):
        self.p = pyaudio.PyAudio()
        self.wf = {}
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.p.terminate()
        del self.p
        try:
            self.wf[0].close()
        except KeyError:
            pass
        del self.wf
    def play(self, i):
        try:
            self.wf[i].close()
            del self.wf[i]
        except KeyError:
            pass
        try:
            self.stream.stop_stream()
            self.stream.close()
            del self.stream
        except AttributeError:
            pass
        self.wf[i] = wave.open(self.arquivos[i], 'rb')
        def callback(in_data, frame_count, time_info, status):
            data = self.wf[i].readframes(frame_count)
            return (data,
                    pyaudio.paContinue if len(data)>0 else pyaudio.paComplete)
        self.stream = self.p.open(
                    format=self.p.get_format_from_width(
                        self.wf[i].getsampwidth()),
                    channels=self.wf[i].getnchannels(),
                    rate=self.wf[i].getframerate(),
                    output=True,
                    stream_callback=callback)
        self.thread = threading.Thread(target=ComparaçãoDialog.controlloop,
                                       args=(self, self.sleep_resolution, i))
        self.thread.deamon = True
        self.thread.start()
    def stop(self, i):
        try:
            self.stream.stop_stream()
            self.stream.close()
            del self.stream
        except AttributeError:
            pass
        self.wf[i].close()
        del self.wf[i]
        time.sleep(1.4*self.sleep_resolution)
        del self.thread
    def complete(self, i):
        j = 1 if i==0 else 0
        self.play_buttons[i].setChecked(False)
        self.listenedto[i] = True
        if False not in self.listenedto:
            self.slide.setDisabled(False)
            self.slidel_label.setDisabled(False)
            self.slider_label.setDisabled(False)
        self.play_buttons[j].setDisabled(False)
    @staticmethod
    def controlloop(dialog, delta, i):
        try:
            while 'stream' in dir(dialog) and dialog.stream.is_active():
                if dialog.givenup:
                    dialog.givenup = False
                    return
                time.sleep(delta)
        except OSError:
            return
        if dialog.givenup:
            dialog.givenup = False
            return
        dialog.complete(i)

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
        self.begin_button.clicked.connect(self.roda_sessao)
        self.save_button.clicked.connect(self.save_result)

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

    def roda_sessao(self):
        self.file_seq.setDisabled()
        with open(self.file_seq.text()) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines if l.strip()!=""]
        self.tipo = lines.pop(0)
        self.testes = []
        for i in range(len(lines)//2):
            self.testes.append([lines[2*i], lines[2*i+1], None])
        i = 0
        while True:
            with ComparaçãoDialog(self, '{}/{}'.format(i+1, len(self.testes)),
                                  self.tipo, self.testes[i], i==0,
                                  self.testes[i][2]) as comparação:
                result = comparação.exec()
            if result==PREV_TEST_CODE:
                if i==0:
                    self.file_seq.setEnabled()
                    del self.tipo
                    del self.testes
                    return
                else:
                    self.testes[i][2] = comparação.slide.value()
                    i -= 1
            elif result==NEXT_TEST_CODE:
                self.testes[i][2] = comparação.slide.value()
                if i+1<len(self.testes):
                    i += 1
                else:
                    break
            else: # ESC
                if i==0:
                    self.file_seq.setEnabled()
                    del self.tipo
                    del self.testes
                    return
                else:
                    i -= 1
        self.save_button.setDisabled(False)
        self.begin_button.setText("Refazer")
        self.towrite  = self.tipo + "\n"
        self.towrite += self.line_tester.text() + "\n"
        self.towrite += self.line_super.text() + "\n"
        for i in range(len(self.testes)):
            self.towrite += "\n{}\n{}\n{}\n".format(*self.testes[i])

    def save_result(self):
        fname = QtGui.QFileDialog.getSaveFileName(
            self, "Escolha um arquivo para salvar os resultados.", os.getcwd())
        with open(fname, "w") as f:
            print(self.towrite, file=f)



def main():

    app = QtGui.QApplication(sys.argv)

    new_font = app.font();
    new_font.setPointSize(15)
    app.setFont(new_font)

    w = SessãoTS()
    w.setFocus()
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
