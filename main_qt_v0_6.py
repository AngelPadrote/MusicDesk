"""MusicDesk v0.6 — interfaz PySide6 refinada.

Reutiliza worker_qt.py y downloader.py sin modificarlos.
Requiere: PySide6, yt-dlp, ffmpeg y ffprobe.

Ejecutar: python main_qt_v0_6.py
"""

import os
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QUrl, Slot
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from worker_qt import HiloDescarga


# También funciona cuando PyInstaller extrae los recursos a sys._MEIPASS.
CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_EMPAQUETADA = Path(getattr(sys, "_MEIPASS", CARPETA_PROYECTO))


def buscar_recurso(nombre):
    """Busca logo en la raíz o en assets/, con o sin empaquetado."""
    for base in (CARPETA_EMPAQUETADA, CARPETA_PROYECTO):
        for carpeta in (base, base / "assets"):
            archivo = carpeta / nombre
            if archivo.is_file():
                return archivo
            if carpeta.is_dir():
                for posible in carpeta.iterdir():
                    if posible.name.casefold() == nombre.casefold() and posible.is_file():
                        return posible
    return None


def preparar_dependencias():
    """Añade al PATH los binarios opcionales incluidos en el ejecutable."""
    if sys.platform != "win32":
        return
    for base in (CARPETA_EMPAQUETADA, CARPETA_PROYECTO):
        if any((base / nombre).is_file() for nombre in ("ffmpeg.exe", "ffprobe.exe", "deno.exe")):
            rutas = os.environ.get("PATH", "").split(os.pathsep)
            if str(base) not in rutas:
                os.environ["PATH"] = str(base) + os.pathsep + os.environ.get("PATH", "")


ESTILOS = """
    QWidget {
        background-color: #10121B;
        color: #F3F2FB;
        font-family: 'Segoe UI';
        font-size: 13px;
    }
    QLabel { background: transparent; }
    QScrollArea { border: none; background: #10121B; }
    QScrollBar:vertical { background: #10121B; width: 9px; margin: 2px; }
    QScrollBar::handle:vertical { background: #3E4257; border-radius: 4px; min-height: 25px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QLabel#nombreApp { font-size: 25px; font-weight: 750; color: #FAF9FF; }
    QLabel#subtitulo { color: #A7ADC2; font-size: 12px; }
    QLabel#version {
        color: #C9B8FF; background-color: #29233E;
        border: 1px solid #453968; border-radius: 12px;
        padding: 5px 11px; font-size: 12px;
    }
    QLabel#logoTexto { background-color: #2B2249; color: #C6A7FF;
        border: 1px solid #4C3D74; border-radius: 16px; font-size: 30px; }
    QFrame#tarjeta, QFrame#progresoTarjeta {
        background-color: #1B1E2A;
        border: 1px solid #323849;
        border-radius: 18px;
    }
    QLabel#tituloSeccion { font-size: 17px; font-weight: 700; color: #F4F2FF; }
    QLabel#descripcionSeccion, QLabel#ayudaCalidad,
    QLabel#pie, QLabel#detalleEstado { color: #A7ADC2; font-size: 12px; }
    QLabel#campo { font-weight: 600; color: #E5E4F0; font-size: 13px; }
    QLineEdit, QComboBox {
        background-color: #111521;
        color: #F5F3FF;
        border: 1px solid #3D4458;
        border-radius: 10px;
        padding: 9px 12px;
        min-height: 24px;
        selection-background-color: #7355D9;
    }
    QLineEdit:hover, QComboBox:hover { border-color: #67617D; }
    QLineEdit:focus, QComboBox:focus { border: 1px solid #A78AFF; }
    QLineEdit:disabled, QComboBox:disabled {
        background-color: #242633; color: #858A9B; border-color: #333746;
    }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox QAbstractItemView {
        background-color: #1F2230; color: #F4F2FF;
        border: 1px solid #51476D;
        selection-background-color: #694CCA;
        selection-color: white;
        padding: 5px;
    }
    QPushButton {
        border: none;
        border-radius: 10px;
        padding: 9px 15px;
        font-weight: 600;
    }
    QPushButton#secundario {
        background-color: #323849; color: #F0EEFA;
        border: 1px solid #40485C;
    }
    QPushButton#secundario:hover { background-color: #41495D; border-color: #686382; }
    QPushButton#pegar { background-color: #292740; color: #D6C8FF; border: 1px solid #51466E; }
    QPushButton#pegar:hover { background-color: #393154; }
    QPushButton#principal {
        background-color: #825BE8;
        color: #FFFFFF; font-size: 15px; font-weight: 700;
        border-radius: 12px;
        padding: 13px;
    }
    QPushButton#principal:hover { background-color: #9876F5; }
    QPushButton#principal:pressed { background-color: #6742C6; }
    QPushButton:disabled { background-color: #292D3B; color: #8A8FA1; border-color: #353846; }
    QProgressBar {
        background-color: #303547;
        border: none;
        border-radius: 6px;
        min-height: 12px;
        max-height: 12px;
    }
    QProgressBar::chunk { background-color: #9872F4; border-radius: 6px; }
    QLabel#porcentaje { color: #D2BDFF; font-size: 17px; font-weight: 750; }
    QLabel#estado { color: #D2D6E6; font-size: 13px; }
    QLabel#insigniaEstado {
        color: #C9B8FF; background: #31264C;
        border-radius: 10px; padding: 4px 10px; font-size: 11px; font-weight: 700;
    }
    QLabel#insigniaEstado[fase="exito"] { color: #A6F2CE; background: #1C473B; }
    QLabel#insigniaEstado[fase="error"] { color: #FFC1C6; background: #522D3A; }
    QLabel#insigniaEstado[fase="trabajando"] { color: #E1D0FF; background: #443061; }
    QToolTip {
        background-color: #2A2B3B; color: #FFFFFF;
        border: 1px solid #66617E; padding: 5px;
    }
"""


class MusicDesk(QWidget):
    def __init__(self):
        super().__init__()
        self.configuracion = QSettings("MusicDesk", "MusicDesk")
        self.hilo = None
        self.convirtiendo = False

        self.setWindowTitle("MusicDesk")
        self.resize(810, 735)
        self.setMinimumSize(670, 585)

        icono = buscar_recurso("MusicDesk.ico") or buscar_recurso("MusicDesk.png")
        if icono:
            self.setWindowIcon(QIcon(str(icono)))

        # El contenido puede desplazarse en pantallas con poca altura.
        contenedor = QWidget()
        principal = QVBoxLayout(contenedor)
        principal.setContentsMargins(29, 24, 29, 18)
        principal.setSpacing(15)
        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        desplazamiento.setWidget(contenedor)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.addWidget(desplazamiento)

        self.crear_cabecera(principal)
        self.crear_formulario(principal)
        self.crear_tarjeta_estado(principal)
        principal.addStretch(1)

        pie = QHBoxLayout()
        ayuda = QLabel("La calidad final depende del audio de origen.")
        ayuda.setObjectName("pie")
        pie.addWidget(ayuda)
        pie.addStretch()
        firma = QLabel("MusicDesk  ·  v0.6")
        firma.setObjectName("pie")
        pie.addWidget(firma)
        principal.addLayout(pie)

        self.setStyleSheet(ESTILOS)

    def crear_cabecera(self, principal):
        cabecera = QHBoxLayout()
        cabecera.setSpacing(13)

        logo = QLabel()
        logo.setObjectName("logoTexto")
        logo.setFixedSize(64, 64)
        logo.setAlignment(Qt.AlignCenter)
        logo_archivo = buscar_recurso("MusicDesk.png") or buscar_recurso("MusicDesk.ico")
        if logo_archivo:
            imagen = QPixmap(str(logo_archivo))
            if not imagen.isNull():
                logo.setPixmap(imagen.scaled(62, 62, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                logo.setText("♫")
        else:
            logo.setText("♫")
        cabecera.addWidget(logo)

        textos = QVBoxLayout()
        textos.setSpacing(3)
        nombre = QLabel("MusicDesk")
        nombre.setObjectName("nombreApp")
        textos.addWidget(nombre)
        subtitulo = QLabel("Tu música, lista para escuchar sin complicaciones")
        subtitulo.setObjectName("subtitulo")
        textos.addWidget(subtitulo)
        cabecera.addLayout(textos)
        cabecera.addStretch()

        version = QLabel("DESCARGADOR MP3")
        version.setObjectName("version")
        cabecera.addWidget(version, alignment=Qt.AlignTop)
        principal.addLayout(cabecera)

    def crear_formulario(self, principal):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(23, 19, 23, 20)
        contenido.setSpacing(7)

        titulo = QLabel("Nueva descarga")
        titulo.setObjectName("tituloSeccion")
        contenido.addWidget(titulo)
        descripcion = QLabel("Pega el enlace, elige una carpeta y descarga tu MP3.")
        descripcion.setObjectName("descripcionSeccion")
        contenido.addWidget(descripcion)
        contenido.addSpacing(3)

        contenido.addWidget(self.etiqueta_campo("Enlace del audio"))
        fila_enlace = QHBoxLayout()
        fila_enlace.setSpacing(9)
        self.url = QLineEdit()
        self.url.setPlaceholderText("Pega aquí un enlace de YouTube...")
        self.url.setClearButtonEnabled(True)
        self.url.setToolTip("Admite enlaces de vídeo y Shorts compatibles con yt-dlp")
        self.url.returnPressed.connect(self.empezar_descarga)
        fila_enlace.addWidget(self.url, 1)
        self.boton_pegar = QPushButton("Pegar")
        self.boton_pegar.setObjectName("pegar")
        self.boton_pegar.setToolTip("Pegar un enlace desde el portapapeles")
        self.boton_pegar.clicked.connect(self.pegar_enlace)
        fila_enlace.addWidget(self.boton_pegar)
        contenido.addLayout(fila_enlace)

        contenido.addSpacing(3)
        contenido.addWidget(self.etiqueta_campo("Carpeta de destino"))
        fila_carpeta = QHBoxLayout()
        fila_carpeta.setSpacing(9)
        self.carpeta = QLineEdit()
        self.carpeta.setPlaceholderText("Selecciona una carpeta de destino")
        self.carpeta.setText(str(self.carpeta_guardada()))
        self.carpeta.setToolTip("Puedes escribir una ruta o elegirla desde el explorador")
        self.carpeta.editingFinished.connect(self.guardar_carpeta)
        fila_carpeta.addWidget(self.carpeta, 1)

        self.boton_carpeta = QPushButton("Elegir...")
        self.boton_carpeta.setObjectName("secundario")
        self.boton_carpeta.setToolTip("Buscar otra carpeta para guardar los MP3")
        self.boton_carpeta.clicked.connect(self.elegir_carpeta)
        fila_carpeta.addWidget(self.boton_carpeta)

        self.boton_abrir = QPushButton("Abrir carpeta")
        self.boton_abrir.setObjectName("secundario")
        self.boton_abrir.setToolTip("Abrir la carpeta actual en el Explorador de Windows")
        self.boton_abrir.clicked.connect(self.abrir_carpeta)
        fila_carpeta.addWidget(self.boton_abrir)
        contenido.addLayout(fila_carpeta)

        contenido.addSpacing(3)
        contenido.addWidget(self.etiqueta_campo("Calidad de audio"))
        self.calidad = QComboBox()
        self.calidad.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.calidad.addItem("Máxima calidad · VBR", "0")
        self.calidad.addItem("Alta calidad · VBR", "2")
        self.calidad.addItem("Equilibrada · 192 kbps", "192")
        self.calidad.addItem("Compacta · 128 kbps", "128")
        valor_previo = str(self.configuracion.value("descargas/calidad", "0"))
        indice = self.calidad.findData(valor_previo)
        self.calidad.setCurrentIndex(indice if indice >= 0 else 0)
        self.calidad.currentIndexChanged.connect(self.guardar_calidad)
        contenido.addWidget(self.calidad)

        self.ayuda_calidad = QLabel()
        self.ayuda_calidad.setObjectName("ayudaCalidad")
        contenido.addWidget(self.ayuda_calidad)
        self.calidad.currentIndexChanged.connect(self.actualizar_ayuda_calidad)
        self.actualizar_ayuda_calidad()

        contenido.addSpacing(4)
        self.boton = QPushButton("Descargar MP3")
        self.boton.setObjectName("principal")
        self.boton.setMinimumHeight(51)
        self.boton.setToolTip("Iniciar la descarga con la calidad seleccionada")
        self.boton.clicked.connect(self.empezar_descarga)
        contenido.addWidget(self.boton)

        principal.addWidget(tarjeta)

    def crear_tarjeta_estado(self, principal):
        tarjeta = QFrame()
        tarjeta.setObjectName("progresoTarjeta")
        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(22, 18, 22, 19)
        contenido.setSpacing(10)
        cabecera = QHBoxLayout()
        titulo = QLabel("Estado de descarga")
        titulo.setObjectName("tituloSeccion")
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        self.insignia = QLabel("LISTO")
        self.insignia.setObjectName("insigniaEstado")
        self.insignia.setProperty("fase", "espera")
        cabecera.addWidget(self.insignia)
        contenido.addLayout(cabecera)

        fila = QHBoxLayout()
        self.estado = QLabel("Esperando un enlace para comenzar.")
        self.estado.setObjectName("estado")
        self.estado.setWordWrap(True)
        fila.addWidget(self.estado, 1)
        self.porcentaje = QLabel("—")
        self.porcentaje.setObjectName("porcentaje")
        fila.addWidget(self.porcentaje)
        contenido.addLayout(fila)

        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        self.barra.setValue(0)
        self.barra.setTextVisible(False)
        contenido.addWidget(self.barra)
        principal.addWidget(tarjeta)

    @staticmethod
    def etiqueta_campo(texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("campo")
        return etiqueta

    def carpeta_guardada(self):
        """Usa la carpeta persistida o Música, si la anterior ya no existe."""
        inicial = Path.home() / "Music"
        if not inicial.is_dir():
            inicial = Path.home()
        valor = str(self.configuracion.value("descargas/ultima_carpeta", str(inicial)))
        ruta = Path(valor).expanduser() if valor.strip() else inicial
        return ruta if ruta.is_dir() else inicial

    def guardar_carpeta(self):
        texto = self.carpeta.text().strip()
        if texto:
            ruta = Path(texto).expanduser()
            if ruta.is_dir():
                self.configuracion.setValue("descargas/ultima_carpeta", str(ruta.resolve()))
                self.configuracion.sync()

    def guardar_calidad(self, *_):
        self.configuracion.setValue("descargas/calidad", str(self.calidad.currentData()))
        self.configuracion.sync()

    def actualizar_ayuda_calidad(self, *_):
        descripcion = {
            "0": "Prioriza la calidad del MP3 con tasa de bits variable.",
            "2": "Buena calidad con archivos generalmente más pequeños.",
            "192": "Tasa de bits fija: 192 kbps.",
            "128": "Tasa de bits fija: 128 kbps; ocupa menos espacio.",
        }
        self.ayuda_calidad.setText(descripcion.get(str(self.calidad.currentData()), ""))

    def elegir_carpeta(self):
        actual = Path(self.carpeta.text().strip()).expanduser()
        inicio = actual if actual.is_dir() else self.carpeta_guardada()
        seleccion = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de descarga", str(inicio))
        if seleccion:
            self.carpeta.setText(seleccion)
            self.guardar_carpeta()

    def abrir_carpeta(self):
        ruta_texto = self.carpeta.text().strip()
        ruta = Path(ruta_texto).expanduser() if ruta_texto else Path()
        if not ruta_texto or not ruta.is_dir():
            QMessageBox.warning(self, "Carpeta no encontrada", "La ruta indicada no existe. Elige una carpeta válida.")
            return
        self.guardar_carpeta()
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(ruta.resolve()))):
            QMessageBox.warning(self, "No se pudo abrir", "No fue posible abrir la carpeta en el explorador.")

    def pegar_enlace(self):
        texto = QApplication.clipboard().text().strip()
        if not texto:
            QMessageBox.information(self, "Portapapeles vacío", "Copia primero un enlace para pegarlo aquí.")
            return
        self.url.setText(texto)
        self.url.setFocus()
        self.url.setCursorPosition(len(texto))

    def marcar_fase(self, texto, fase):
        self.insignia.setText(texto)
        self.insignia.setProperty("fase", fase)
        self.insignia.style().unpolish(self.insignia)
        self.insignia.style().polish(self.insignia)
        self.insignia.update()

    def activar_controles(self, habilitados):
        for control in (self.url, self.carpeta, self.calidad, self.boton, self.boton_carpeta, self.boton_pegar):
            control.setEnabled(habilitados)
        # Abrir carpeta se mantiene disponible aunque se esté descargando.

    def empezar_descarga(self):
        if self.hilo is not None:
            return

        enlace = self.url.text().strip()
        carpeta_texto = self.carpeta.text().strip()
        destino = Path(carpeta_texto).expanduser() if carpeta_texto else None
        calidad = str(self.calidad.currentData())

        if not enlace.startswith(("https://", "http://")):
            QMessageBox.warning(self, "Enlace no válido", "Pega una URL que empiece por https:// o http://.")
            self.url.setFocus()
            return
        if destino is None or not destino.is_dir():
            QMessageBox.warning(self, "Carpeta no válida", "Selecciona una carpeta existente donde guardar el MP3.")
            self.carpeta.setFocus()
            return
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            QMessageBox.critical(
                self, "Falta FFmpeg",
                "MusicDesk necesita ffmpeg y ffprobe para generar MP3.\n"
                "Comprueba que ambos estén disponibles en el PATH de Windows."
            )
            return

        self.guardar_carpeta()
        self.guardar_calidad()
        self.convirtiendo = False
        self.barra.setRange(0, 100)
        self.barra.setValue(0)
        self.porcentaje.setText("0%")
        self.estado.setText("Preparando la descarga...")
        self.marcar_fase("INICIANDO", "trabajando")
        self.activar_controles(False)

        self.hilo = HiloDescarga(enlace, str(destino), calidad, self)
        self.hilo.progreso.connect(self.actualizar_progreso)
        self.hilo.estado.connect(self.actualizar_estado)
        self.hilo.completado.connect(self.descarga_completada)
        self.hilo.error.connect(self.descarga_error)
        self.hilo.finished.connect(self.hilo_finalizado)
        self.hilo.start()

    @Slot(int)
    def actualizar_progreso(self, porcentaje):
        if self.convirtiendo:
            return
        valor = max(0, min(100, int(porcentaje)))
        self.barra.setValue(valor)
        self.porcentaje.setText(f"{valor}%")
        self.estado.setText("Descargando el audio...")
        self.marcar_fase("DESCARGANDO", "trabajando")

    @Slot(str)
    def actualizar_estado(self, mensaje):
        self.estado.setText(mensaje)
        if "convirt" in mensaje.lower() or "procesando" in mensaje.lower():
            # En esta fase yt-dlp/FFmpeg no ofrece un porcentaje preciso.
            self.convirtiendo = True
            self.barra.setRange(0, 0)
            self.porcentaje.setText("…")
            self.marcar_fase("CONVIRTIENDO", "trabajando")

    @Slot()
    def descarga_completada(self):
        self.barra.setRange(0, 100)
        self.barra.setValue(100)
        self.porcentaje.setText("100%")
        self.estado.setText("¡MP3 guardado! Puedes abrir la carpeta para escucharlo.")
        self.marcar_fase("COMPLETADO", "exito")

    @Slot(str)
    def descarga_error(self, mensaje):
        self.barra.setRange(0, 100)
        self.barra.setValue(0)
        self.porcentaje.setText("—")
        self.estado.setText("No se pudo completar la descarga.")
        self.marcar_fase("ERROR", "error")
        QMessageBox.critical(self, "Error de descarga", mensaje)

    @Slot()
    def hilo_finalizado(self):
        self.activar_controles(True)
        if self.hilo is not None:
            self.hilo.wait()
            self.hilo = None

    def closeEvent(self, evento):
        if self.hilo is not None and self.hilo.isRunning():
            QMessageBox.information(
                self, "Descarga en curso",
                "La descarga sigue en proceso. Espera a que termine para cerrar MusicDesk."
            )
            evento.ignore()
            return
        evento.accept()


if __name__ == "__main__":
    preparar_dependencias()
    app = QApplication(sys.argv)
    app.setApplicationName("MusicDesk")
    app.setOrganizationName("MusicDesk")
    icono = buscar_recurso("MusicDesk.ico") or buscar_recurso("MusicDesk.png")
    if icono:
        app.setWindowIcon(QIcon(str(icono)))
    ventana = MusicDesk()
    ventana.show()
    sys.exit(app.exec())
