# Leitor de Vídeo Qt multiplataforma (Windows 10, Ubuntu, macOS)
# Requisitos: Python 3.9+, PySide6 (Qt6)
# Instalar:  pip install PySide6
# Execução:  python leitor_video_qt.py

import sys
import os
import shutil
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox,
    QToolBar, QStyle, QSlider, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QStatusBar
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leitor de Vídeo Qt")
        self.resize(1000, 640)

        # Estado
        self.current_url: QUrl | None = None
        self.current_local_path: Path | None = None  # caminho do ficheiro aberto (se local)
        self.save_path: Path | None = None  # destino para "Guardar"

        # Media
        self.audio = QAudioOutput()
        self.audio.setVolume(0.5)
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio)

        # UI vídeo
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        # Controlo playback
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
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(50)
        self.volume.valueChanged.connect(lambda v: self.audio.setVolume(v/100))

        controls = QHBoxLayout()
        controls.setContentsMargins(8, 8, 8, 8)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(QLabel("Posição"))
        controls.addWidget(self.position, 1)
        controls.addWidget(self.time_label)
        controls.addWidget(QLabel("Volume"))
        controls.addWidget(self.volume)

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(self.video_widget, 1)
        central_layout.addLayout(controls)
        self.setCentralWidget(central)

        # Conexões de media
        self.player.playbackStateChanged.connect(self._sync_play_icon)
        self.player.durationChanged.connect(self._on_duration)
        self.player.positionChanged.connect(self._on_position)
        self.player.errorOccurred.connect(self._on_error)

        # Menu e toolbar
        self._build_menus_and_toolbar()

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    # --- Menus e Toolbar ---
    def _build_menus_and_toolbar(self):
        file_menu = self.menuBar().addMenu("&Ficheiro")
        view_menu = self.menuBar().addMenu("&Ver")
        help_menu = self.menuBar().addMenu("&Ajuda")

        style = self.style()
        ic_open = style.standardIcon(QStyle.SP_DialogOpenButton)
        ic_save = style.standardIcon(QStyle.SP_DialogSaveButton)
        ic_save_as = style.standardIcon(QStyle.SP_DriveFDIcon)
        ic_delete = style.standardIcon(QStyle.SP_TrashIcon)
        ic_exit = style.standardIcon(QStyle.SP_DialogCloseButton)
        ic_fullscreen = style.standardIcon(QStyle.SP_TitleBarMaxButton)
        ic_about = style.standardIcon(QStyle.SP_MessageBoxInformation)
        ic_url = style.standardIcon(QStyle.SP_BrowserReload)  # reutilizado para Abrir URL

        self.act_open = QAction(ic_open, "Abrir…", self)
        self.act_open.setShortcut("Ctrl+O")
        self.act_open.triggered.connect(self.open_file)

        self.act_open_url = QAction(ic_url, "Abrir URL…", self)
        self.act_open_url.triggered.connect(self.open_url)

        self.act_save = QAction(ic_save, "Guardar", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.triggered.connect(self.save_copy)

        self.act_save_as = QAction(ic_save_as, "Guardar como…", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.act_save_as.triggered.connect(self.save_copy_as)

        self.act_delete = QAction(ic_delete, "Apagar ficheiro…", self)
        self.act_delete.triggered.connect(self.delete_file)

        self.act_exit = QAction(ic_exit, "Sair", self)
        self.act_exit.setShortcut("Ctrl+Q")
        self.act_exit.triggered.connect(self.close)

        self.act_fullscreen = QAction(ic_fullscreen, "Ecrã inteiro", self, checkable=True)
        self.act_fullscreen.setShortcut("F11")
        self.act_fullscreen.triggered.connect(self.toggle_fullscreen)

        self.act_about = QAction(ic_about, "Sobre", self)
        self.act_about.triggered.connect(self.show_about)

        for a in [self.act_open, self.act_open_url, self.act_save, self.act_save_as, self.act_delete, self.act_exit]:
            file_menu.addAction(a)
        view_menu.addAction(self.act_fullscreen)
        help_menu.addAction(self.act_about)

        # Toolbar
        tb = QToolBar("Principal")
        tb.setMovable(False)
        self.addToolBar(tb)
        for a in [self.act_open, self.act_open_url, self.act_save, self.act_save_as, self.act_delete]:
            tb.addAction(a)
        tb.addSeparator()
        # Botões de reprodução na toolbar (útil em ecrã inteiro)
        act_play = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), "Reproduzir/Pausa", self)
        act_play.triggered.connect(self.toggle_play)
        tb.addAction(act_play)
        act_stop = QAction(self.style().standardIcon(QStyle.SP_MediaStop), "Parar", self)
        act_stop.triggered.connect(self.player.stop)
        tb.addAction(act_stop)

    # --- Ações ---
    def open_file(self):
        filters = (
            "Vídeo (*.mp4 *.mkv *.avi *.mov *.m4v *.wmv *.webm);;Todos os ficheiros (*.*)"
        )
        path, _ = QFileDialog.getOpenFileName(self, "Abrir vídeo", str(Path.home()), filters)
        if not path:
            return
        url = QUrl.fromLocalFile(path)
        self._load_media(url)
        self.current_local_path = Path(path)
        self.save_path = None
        self.status.showMessage(f"Aberto: {path}", 5000)

    def open_url(self):
        # Diálogo simples usando getText para URL
        from PySide6.QtWidgets import QInputDialog
        url_text, ok = QInputDialog.getText(self, "Abrir URL", "Introduza o URL do vídeo/stream:")
        if not ok or not url_text:
            return
        url = QUrl(url_text)
        if not url.isValid():
            QMessageBox.warning(self, "URL inválido", "O URL não é válido.")
            return
        self._load_media(url)
        self.current_local_path = None
        self.save_path = None
        self.status.showMessage(f"Aberto URL: {url.toString()}", 5000)

    def save_copy(self):
        if not self.current_local_path:
            # Se o ficheiro corrente não é local, exigir "Guardar como"
            QMessageBox.information(self, "Guardar", "Nada para guardar aqui. Use 'Guardar como…' para copiar.")
            self.save_copy_as()
            return
        if not self.save_path:
            self.save_copy_as()
            return
        try:
            shutil.copy2(self.current_local_path, self.save_path)
            self.status.showMessage(f"Guardado em: {self.save_path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao guardar", str(e))

    def save_copy_as(self):
        if self.current_local_path:
            default_name = self.current_local_path.name
        else:
            default_name = "video.mp4"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar como…", str(Path.home() / default_name))
        if not path:
            return
        self.save_path = Path(path)
        if self.current_local_path:
            # Copiar do ficheiro aberto
            try:
                shutil.copy2(self.current_local_path, self.save_path)
                self.status.showMessage(f"Guardado em: {self.save_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Erro ao guardar", str(e))
        else:
            # Se for stream/URL, não há origem local. Avisar.
            QMessageBox.information(self, "Guardar como…", "O conteúdo é um stream/URL; não é possível copiar sem origem local.")

    def delete_file(self):
        if not self.current_local_path or not self.current_local_path.exists():
            QMessageBox.information(self, "Apagar ficheiro", "Nenhum ficheiro local aberto para apagar.")
            return
        reply = QMessageBox.question(
            self,
            "Confirmar apagar",
            f"Tem a certeza que pretende apagar:\n{self.current_local_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.player.stop()
                os.remove(self.current_local_path)
                self.status.showMessage("Ficheiro apagado.", 5000)
                self.current_local_path = None
                self.current_url = None
                self.player.setSource(QUrl())
                self.time_label.setText("00:00 / 00:00")
                self.position.setRange(0, 0)
            except Exception as e:
                QMessageBox.critical(self, "Erro ao apagar", str(e))

    def toggle_fullscreen(self, checked: bool):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def show_about(self):
        QMessageBox.information(
            self,
            "Sobre",
            "Leitor de Vídeo Qt\n\n"
            "- Multiplataforma: Windows, Ubuntu, macOS\n"
            "- Abrir ficheiro local ou URL/stream\n"
            "- Guardar cópia, Guardar como, Apagar ficheiro\n"
            "- Controlo de reprodução, volume e ecrã inteiro"
        )

    # --- Reprodução ---
    def _load_media(self, url: QUrl):
        self.current_url = url
        self.player.setSource(url)
        # Iniciar reprodução automaticamente após pequeno atraso para garantir preparação
        QTimer.singleShot(100, self.player.play)
        self._sync_play_icon()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _sync_play_icon(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def _on_duration(self, duration_ms: int):
        self.position.setRange(0, duration_ms)
        self._update_time_label(self.player.position(), duration_ms)

    def _on_position(self, pos_ms: int):
        if not self.position.isSliderDown():
            self.position.setValue(pos_ms)
        self._update_time_label(pos_ms, self.player.duration())

    @staticmethod
    def _format_ms(ms: int) -> str:
        secs = max(0, int(ms / 1000))
        h, r = divmod(secs, 3600)
        m, s = divmod(r, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _update_time_label(self, pos_ms: int, dur_ms: int):
        self.time_label.setText(f"{self._format_ms(pos_ms)} / {self._format_ms(dur_ms)}")

    def _on_error(self, err, what):
        # Qt6: errorOccurred(self, error, errorString)
        # Alguns formatos podem exigir codecs do sistema.
        QMessageBox.warning(self, "Erro de reprodução", f"{what}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Leitor de Vídeo Qt")
    w = VideoPlayer()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
