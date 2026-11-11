"""Genera MusicDesk.exe con PyInstaller desde Windows y el entorno virtual."""

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def buscar(nombre):
    for carpeta in (BASE, BASE / "assets"):
        archivo = carpeta / nombre
        if archivo.is_file():
            return archivo
    return None


def main():
    if sys.platform != "win32":
        raise SystemExit("Esta compilación debe realizarse desde Windows.")
    for modulo in ("PyInstaller", "PySide6", "yt_dlp"):
        if importlib.util.find_spec(modulo) is None:
            raise SystemExit(f"Falta {modulo}. Instálalo en tu entorno virtual.")
    for archivo in ("main_qt_v0_6.py", "downloader.py", "worker_qt.py"):
        if not (BASE / archivo).is_file():
            raise SystemExit(f"Falta {archivo}. Copia este script junto a tu proyecto.")

    comando = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", "MusicDesk", "--collect-submodules", "yt_dlp",
    ]

    ico = buscar("MusicDesk.ico")
    png = buscar("MusicDesk.png")
    if ico:
        comando.extend(["--icon", str(ico)])
    else:
        print("AVISO: no se encontró MusicDesk.ico. Se usará el icono predeterminado.")
    for recurso in (ico, png):
        if recurso:
            comando.extend(["--add-data", str(recurso) + os.pathsep + "."])

    if importlib.util.find_spec("yt_dlp_ejs") is not None:
        comando.extend(["--collect-all", "yt_dlp_ejs"])

    for nombre in ("ffmpeg.exe", "ffprobe.exe", "deno.exe"):
        ruta = buscar(nombre)
        if not ruta:
            encontrada = shutil.which(nombre)
            ruta = Path(encontrada) if encontrada else None
        if ruta:
            comando.extend(["--add-binary", str(ruta.resolve()) + os.pathsep + "."])
            print("Se incluirá:", nombre)
        else:
            print("AVISO:", nombre, "no está disponible para empaquetar.")

    comando.append(str(BASE / "main_qt_v0_6.py"))
    print("\nCompilando MusicDesk...\n")
    resultado = subprocess.run(comando, cwd=BASE, check=False)
    if resultado.returncode:
        raise SystemExit(f"Error de PyInstaller: {resultado.returncode}")
    print("\nAplicación generada en:", BASE / "dist" / "MusicDesk.exe")


if __name__ == "__main__":
    main()
