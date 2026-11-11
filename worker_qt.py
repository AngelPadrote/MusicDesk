"""Conecta los eventos de downloader.py con las senales de Qt."""

from PySide6.QtCore import QThread, Signal
from downloader import descargar_mp3


class PuenteEventos:
    """Adaptador: downloader.py llama a .put((tipo, valor))."""

    def __init__(self, hilo):
        self.hilo = hilo

    def put(self, evento):
        tipo, valor = evento
        if tipo == "progreso":
            self.hilo.progreso.emit(int(valor))
        elif tipo == "estado":
            self.hilo.estado.emit(str(valor))


class HiloDescarga(QThread):
    progreso = Signal(int)
    estado = Signal(str)
    completado = Signal()
    error = Signal(str)

    def __init__(self, url, carpeta, calidad, parent=None):
        super().__init__(parent)
        self.url = url
        self.carpeta = carpeta
        self.calidad = calidad

    def run(self):
        """Qt ejecuta run() fuera del hilo de la interfaz."""
        try:
            # El motor sigue siendo independiente de Qt. No lo reescribimos.
            descargar_mp3(
                self.url,
                self.carpeta,
                self.calidad,
                PuenteEventos(self)
            )
        except Exception as exc:
            self.error.emit(str(exc))
        else:
            self.completado.emit()
