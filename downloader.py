from pathlib import Path
from yt_dlp import YoutubeDL


def descargar_mp3(url, carpeta, calidad, eventos):
    """Descarga el audio y comunica avances a la interfaz por una cola."""

    def reportar_progreso(datos):
        if datos["status"] == "downloading":
            total = datos.get("total_bytes") or datos.get("total_bytes_estimate")
            recibido = datos.get("downloaded_bytes", 0)

            if total:
                porcentaje = min(100, int(recibido * 100 / total))
                eventos.put(("progreso", porcentaje))

        elif datos["status"] == "finished":
            eventos.put(("estado", "Audio descargado. Convirtiendo a MP3..."))

    opciones = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(carpeta) / "%(title).150B [%(id)s].%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "progress_hooks": [reportar_progreso],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": calidad,
        }],
    }

    with YoutubeDL(opciones) as ydl:
        resultado = ydl.download([url])

    if resultado != 0:
        raise RuntimeError("yt-dlp no pudo completar la descarga.")
