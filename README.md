# Video-Viewer
- Editor / Exibidor de Vídeo simples usando PyQt5
- Funcionalidades:
 - Menu: Ficheiro -> Abrir, Sair
 - Botões: Ligar (Play), Pausa (Pause), Desligar (Stop)
 - Slider de progresso, rótulo com tempo, controlo de volume

- Instruções:
 1) Instalar dependências: pip install PyQt5
 2) Executar: python Video-Viewer.py

Compatível com Windows, Linux e macOS (desde que PyQt5 esteja instalado).
---
O **`QMediaPlayer`** é uma classe do **PyQt5.QtMultimedia** (ou PySide6.QtMultimedia) que serve para **reproduzir ficheiros de áudio e vídeo** dentro de aplicações Qt.

Ele funciona como o “motor” de reprodução, e tu ligas esse motor a um “ecrã” (`QVideoWidget`) para mostrar o vídeo.

---

## 📦 O que o QMediaPlayer faz

* **Carregar ficheiros** (locais ou online) através de `QMediaContent` e `QUrl`.
* **Controlar reprodução**: `play()`, `pause()`, `stop()`.
* **Avançar / recuar** no vídeo: `setPosition(ms)`.
* **Definir volume**: `setVolume(valor)`.
* **Obter estado**: parado, a reproduzir, em pausa.
* **Obter tempo atual e duração** para mostrar na interface.

---

## 🔌 Como usar

1. **Criar o player**

```python
from PyQt5.QtMultimedia import QMediaPlayer
player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
```

O segundo argumento (`QMediaPlayer.VideoSurface`) indica que vamos enviar vídeo para um widget.

2. **Criar o ecrã de vídeo**

```python
from PyQt5.QtMultimediaWidgets import QVideoWidget
videoWidget = QVideoWidget()
player.setVideoOutput(videoWidget)
```

3. **Carregar ficheiro**

```python
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent

url = QUrl.fromLocalFile("/caminho/para/video.mp4")
player.setMedia(QMediaContent(url))
```

4. **Controlar**

```python
player.play()   # Ligar
player.pause()  # Pausar
player.stop()   # Parar
```

---

## 📡 Sinais (Signals)

O `QMediaPlayer` envia sinais quando algo muda:

* `stateChanged(state)` → muda de Playing, Paused, Stopped.
* `positionChanged(ms)` → a posição atual mudou.
* `durationChanged(ms)` → a duração do ficheiro foi detetada.
* `error(error)` → ocorreu um erro.

Estes sinais servem para atualizar botões, sliders e rótulos na GUI.

---

## ⚠️ Limitações

* No **Windows**, depende dos codecs do sistema (Media Foundation).
* Pode não abrir certos formatos (MKV, FLV, WebM) sem os codecs corretos.
* Para suporte universal, normalmente usamos **`python-vlc`**.

Queres que eu faça essa comparação?

