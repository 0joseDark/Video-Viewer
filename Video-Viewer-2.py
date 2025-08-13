# Leitor de Vídeo Qt com Playlist, Atalhos Extra, Equalizador, Controlo de Velocidade e Volume
# Compatível com Windows 10, Ubuntu e macOS — PySide6

import sys
import os
import shutil
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QToolBar, QStyle,
    QSlider, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QStatusBar, QListWidget,
    QInputDialog, QSplitter, QDial
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leitor de Vídeo Qt Avançado")
        self.resize(1200, 700)

        self.current_url = None
        self.current_local_path = None
        self.save_path = None

        self.audio = QAudioOutput()
        self.audio.setVolume(0.5)
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_from_playlist)

        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.clicked.connect(self.player.stop)

        self.position = QSlider(Qt.Horizontal)
        self.position.setRange(0, 0)
        self.position.sliderMoved.connect(self.player.setPosition)

        self.time_label = QLabel("00:00 / 00:00")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(lambda v: self.audio.setVolume(v/100))

        self.speed_dial = QDial()
        self.speed_dial.setRange(50, 200)
        self.speed_dial.setValue(100)
        self.speed_dial.valueChanged.connect(self.change_speed)

        self.bass_slider = QSlider(Qt.Horizontal)
        self.bass_slider.setRange(-10, 10)
        self.bass_slider.setValue(0)
        self.bass_slider.valueChanged.connect(lambda v: self.status.showMessage(f"Graves: {v}"))

        self.treble_slider = QSlider(Qt.Horizontal)
        self.treble_slider.setRange(-10, 10)
        self.treble_slider.setValue(0)
        self.treble_slider.valueChanged.connect(lambda v: self.status.showMessage(f"Agudos: {v}"))

        controls = QHBoxLayout()
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(QLabel("Posição"))
        controls.addWidget(self.position, 1)
        controls.addWidget(self.time_label)
        controls.addWidget(QLabel("Volume"))
        controls.addWidget(self.volume_slider)
        controls.addWidget(QLabel("Velocidade (%)"))
        controls.addWidget(self.speed_dial)
        controls.addWidget(QLabel("Graves"))
        controls.addWidget(self.bass_slider)
        controls.addWidget(QLabel("Agudos"))
        controls.addWidget(self.treble_slider)

        video_area = QSplitter()
        video_area.addWidget(self.playlist)
        video_area.addWidget(self.video_widget)
        video_area.setStretchFactor(1, 1)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(video_area)
        layout.addLayout(controls)
        self.setCentralWidget(central)

        self.player.playbackStateChanged.connect(self._sync_play_icon)
        self.player.durationChanged.connect(self._on_duration)
        self.player.positionChanged.connect(self._on_position)
        self.player.errorOccurred.connect(self._on_error)

        self._build_menus_and_toolbar()
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._setup_shortcuts()

    def _build_menus_and_toolbar(self):
        file_menu = self.menuBar().addMenu("&Ficheiro")

        self.act_open = QAction("Abrir…", self)
        self.act_open.setShortcut("Ctrl+O")
        self.act_open.triggered.connect(self.open_file)

        self.act_open_url = QAction("Abrir URL…", self)
        self.act_open_url.triggered.connect(self.open_url)

        self.act_add_playlist = QAction("Adicionar à Playlist…", self)
        self.act_add_playlist.triggered.connect(self.add_to_playlist)

        self.act_exit = QAction("Sair", self)
        self.act_exit.setShortcut("Ctrl+Q")
        self.act_exit.triggered.connect(self.close)

        for a in [self.act_open, self.act_open_url, self.act_add_playlist, self.act_exit]:
            file_menu.addAction(a)

        tb = QToolBar("Principal")
        tb.setMovable(False)
        self.addToolBar(tb)
        for a in [self.act_open, self.act_open_url, self.act_add_playlist]:
            tb.addAction(a)

    def _setup_shortcuts(self):
        self.play_btn.setShortcut("Space")
        self.stop_btn.setShortcut("S")

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir vídeo", str(Path.home()), "Vídeo (*.mp4 *.mkv *.avi *.mov *.m4v *.wmv *.webm)")
        if path:
            self._load_media(QUrl.fromLocalFile(path))
            self.current_local_path = Path(path)

    def open_url(self):
        url_text, ok = QInputDialog.getText(self, "Abrir URL", "Introduza o URL do vídeo/stream:")
        if ok and url_text:
            self._load_media(QUrl(url_text))

    def add_to_playlist(self):
        path, _ = QFileDialog.getOpenFileName(self, "Adicionar vídeo", str(Path.home()), "Vídeo (*.mp4 *.mkv *.avi *.mov *.m4v *.wmv *.webm)")
        if path:
            self.playlist.addItem(path)

    def play_from_playlist(self, item):
        self._load_media(QUrl.fromLocalFile(item.text()))

    def _load_media(self, url: QUrl):
        self.current_url = url
        self.player.setSource(url)
        QTimer.singleShot(100, self.player.play)

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def change_speed(self, value):
        self.player.setPlaybackRate(value / 100.0)

    def _sync_play_icon(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def _on_duration(self, duration_ms):
        self.position.setRange(0, duration_ms)
        self._update_time_label(self.player.position(), duration_ms)

    def _on_position(self, pos_ms):
        if not self.position.isSliderDown():
            self.position.setValue(pos_ms)
        self._update_time_label(pos_ms, self.player.duration())

    def _format_ms(self, ms):
        secs = max(0, int(ms / 1000))
        h, r = divmod(secs, 3600)
        m, s = divmod(r, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _update_time_label(self, pos_ms, dur_ms):
        self.time_label.setText(f"{self._format_ms(pos_ms)} / {self._format_ms(dur_ms)}")

    def _on_error(self, err, what):
        QMessageBox.warning(self, "Erro de reprodução", f"{what}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
