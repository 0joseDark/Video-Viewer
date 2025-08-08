#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QAction, QFileDialog, QSlider, QLabel, QStyle, QStatusBar,
    QMessageBox)
from PyQt5.QtCore import Qt, QUrl, QTime, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


class VideoEditorViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor / Exibidor de Vídeo - Qt")
        self.resize(900, 600)

        # Player e widget de vídeo
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Controlo de reprodução
        self.playButton = QPushButton("Ligar")
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.play)

        self.pauseButton = QPushButton("Pausa")
        self.pauseButton.setEnabled(False)
        self.pauseButton.clicked.connect(self.pause)

        self.stopButton = QPushButton("Desligar")
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stop)

        # Slider de progresso
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Rótulo de tempo
        self.timeLabel = QLabel("00:00 / 00:00")

        # Volume
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setFixedWidth(120)
        self.volumeSlider.valueChanged.connect(self.setVolume)

        self.volumeLabel = QLabel("Vol:")

        # Layout dos botões
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.pauseButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addStretch(1)
        controlLayout.addWidget(self.timeLabel)
        controlLayout.addStretch(1)
        controlLayout.addWidget(self.volumeLabel)
        controlLayout.addWidget(self.volumeSlider)

        # Layout principal
        widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addWidget(self.positionSlider)
        layout.addLayout(controlLayout)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Menu
        openAction = QAction("Abrir…", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.openFile)

        exitAction = QAction("Sair", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("Ficheiro")
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # Barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Ligações do mediaPlayer aos eventos
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        # Timer para actualizar tempo (opcional, mais suave)
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.updateTimeLabel)

        # Ficheiro aberto
        self.currentFile = None

    # --- Ações do menu / botões ---
    def openFile(self):
        """Abre um diálogo para escolher um ficheiro de vídeo local."""
        fname, _ = QFileDialog.getOpenFileName(self, "Abrir ficheiro de vídeo", str(Path.home()),
                                              "Vídeos (*.mp4 *.avi *.mkv *.mov);;Todos os ficheiros (*)")
        if fname:
            self.loadFile(fname)

    def loadFile(self, filename: str):
        """Carrega o ficheiro no QMediaPlayer."""
        url = QUrl.fromLocalFile(filename)
        content = QMediaContent(url)
        self.mediaPlayer.setMedia(content)
        self.currentFile = filename
        self.playButton.setEnabled(True)
        self.pauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.statusBar.showMessage(f"Ficheiro carregado: {filename}")
        # Auto-play ao carregar
        self.play()

    def play(self):
        if self.mediaPlayer.mediaStatus() == QMediaPlayer.NoMedia:
            self.statusBar.showMessage("Nenhum ficheiro carregado.")
            return
        self.mediaPlayer.play()
        self.timer.start()

    def pause(self):
        self.mediaPlayer.pause()
        self.timer.stop()

    def stop(self):
        self.mediaPlayer.stop()
        self.timer.stop()
        # Repor slider para início
        self.positionSlider.setValue(0)

    # --- Eventos do player ---
    def mediaStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playButton.setEnabled(False)
            self.pauseButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.statusBar.showMessage("A reproduzir")
        elif state == QMediaPlayer.PausedState:
            self.playButton.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.statusBar.showMessage("Em pausa")
        else:
            # StoppedState ou outro
            self.playButton.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.statusBar.showMessage("Parado")

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.updateTimeLabel()

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.updateTimeLabel()

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setVolume(self, value):
        self.mediaPlayer.setVolume(value)

    def updateTimeLabel(self):
        pos = self.mediaPlayer.position() // 1000  # segundos
        dur = self.mediaPlayer.duration() // 1000  # segundos
        pos_time = QTime(0, 0, 0).addSecs(int(pos)).toString('hh:mm:ss')
        dur_time = QTime(0, 0, 0).addSecs(int(dur)).toString('hh:mm:ss')
        if dur == 0:
            dur_time = "00:00"
        self.timeLabel.setText(f"{pos_time} / {dur_time}")

    def handleError(self, error):
        # Mostrar mensagem de erro simples
        err = self.mediaPlayer.errorString()
        if err:
            QMessageBox.critical(self, "Erro de reprodução", err)
        else:
            QMessageBox.critical(self, "Erro de reprodução", "Erro desconhecido no QMediaPlayer.")


def main():
    app = QApplication(sys.argv)
    window = VideoEditorViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
