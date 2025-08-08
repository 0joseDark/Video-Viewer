#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Editor / Exibidor de Vídeo com Qt e python-vlc
------------------------------------------------
Agora com:
 - Controlo de volume
 - Modo fullscreen
 - Suporte a streams online (URLs)

Instalação:
 pip install PyQt5 python-vlc

Execução:
 python editor_exibidor_video_vlc.py
"""

import sys
import vlc
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QAction, QFileDialog, QSlider, QLabel, QStatusBar, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer

class VideoPlayerVLC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor / Exibidor de Vídeo - VLC + Qt")
        self.resize(900, 600)

        # Instância do VLC
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Widget de vídeo
        self.video_frame = QWidget(self)
        self.video_frame.setStyleSheet("background-color: black;")

        # Botões de controlo
        self.playButton = QPushButton("Ligar")
        self.playButton.clicked.connect(self.play_video)
        self.pauseButton = QPushButton("Pausa")
        self.pauseButton.clicked.connect(self.pause_video)
        self.stopButton = QPushButton("Desligar")
        self.stopButton.clicked.connect(self.stop_video)
        self.fullscreenButton = QPushButton("Fullscreen")
        self.fullscreenButton.clicked.connect(self.toggle_fullscreen)

        # Slider de progresso
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 1000)
        self.positionSlider.sliderMoved.connect(self.set_position)

        # Slider de volume
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.valueChanged.connect(self.set_volume)
        self.set_volume(50)

        # Rótulos
        self.timeLabel = QLabel("00:00 / 00:00")
        self.volumeLabel = QLabel("Vol:")

        # Layout dos controlos
        controls = QHBoxLayout()
        controls.addWidget(self.playButton)
        controls.addWidget(self.pauseButton)
        controls.addWidget(self.stopButton)
        controls.addWidget(self.fullscreenButton)
        controls.addWidget(self.timeLabel)
        controls.addStretch(1)
        controls.addWidget(self.volumeLabel)
        controls.addWidget(self.volumeSlider)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.video_frame)
        layout.addWidget(self.positionSlider)
        layout.addLayout(controls)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Menu
        fileMenu = self.menuBar().addMenu("Ficheiro")

        openAction = QAction("Abrir ficheiro…", self)
        openAction.triggered.connect(self.open_file)

        streamAction = QAction("Abrir stream online…", self)
        streamAction.triggered.connect(self.open_stream)

        exitAction = QAction("Sair", self)
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(openAction)
        fileMenu.addAction(streamAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # Barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Timer para atualização
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_ui)

        self.media = None
        self.is_fullscreen = False

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Abrir ficheiro de vídeo", str(Path.home()),
            "Vídeos (*.mp4 *.mkv *.avi *.mov *.flv *.webm);;Todos os ficheiros (*)")
        if filename:
            self.load_video(filename)

    def open_stream(self):
        url, ok = QInputDialog.getText(self, "Abrir stream", "Introduza o URL do vídeo/stream:")
        if ok and url:
            self.load_video(url)

    def load_video(self, path_or_url):
        self.media = self.instance.media_new(path_or_url)
        self.media_player.set_media(self.media)

        if sys.platform.startswith('linux'):
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":
            self.media_player.set_nsobject(int(self.video_frame.winId()))

        self.statusBar.showMessage(f"Carregado: {path_or_url}")
        self.play_video()

    def play_video(self):
        if self.media is None:
            QMessageBox.warning(self, "Aviso", "Nenhum ficheiro ou stream carregado")
            return
        self.media_player.play()
        self.timer.start()

    def pause_video(self):
        self.media_player.pause()

    def stop_video(self):
        self.media_player.stop()
        self.timer.stop()
        self.positionSlider.setValue(0)
        self.timeLabel.setText("00:00 / 00:00")

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)

    def set_position(self, position):
        self.media_player.set_position(position / 1000.0)

    def update_ui(self):
        length = self.media_player.get_length() / 1000
        current = self.media_player.get_time() / 1000

        if length > 0:
            pos = int(self.media_player.get_position() * 1000)
            self.positionSlider.setValue(pos)

        cur_time = self.format_time(current)
        total_time = self.format_time(length)
        self.timeLabel.setText(f"{cur_time} / {total_time}")

    @staticmethod
    def format_time(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"


def main():
    app = QApplication(sys.argv)
    player = VideoPlayerVLC()
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
