"""
Build script for Trick Runner.

Usage:
    py -3 build.py

Output structure:
    dist/
        trick runner/
            trick runner.exe        ← PyInstaller onefile, windowed (no console)
            leiame.txt
            lib/
                sounds/             ← .ogg audio files
                accessible_output2/ ← screen-reader DLLs + Python source
                sound_lib/          ← BASS DLLs + Python source
        trick runner.zip            ← distributable archive of the folder above

Notes:
- Python code (including sound_lib and accessible_output2 modules) is bundled
  inside the exe via --collect-submodules so their DLLs are NOT duplicated
  inside the exe.
- At runtime the exe finds DLLs and sounds in lib/ (next to itself) thanks to
  the patches in sound_lib/external/paths.py, accessible_output2/__init__.py,
  and constants.py.
"""
import os
import shutil
import subprocess
import sys
import zipfile

GAME_NAME = "trick runner"
DIST_DIR  = "dist"
GAME_DIR  = os.path.join(DIST_DIR, GAME_NAME)

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def run_pyinstaller() -> None:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--name", GAME_NAME,
        "--collect-submodules", "accessible_output2",
        "--collect-submodules", "sound_lib",
        "--distpath", GAME_DIR,
        "--workpath", "build",
        "--specpath", ".",
        "main.py",
    ]
    print("Executando PyInstaller…")
    subprocess.run(cmd, check=True)


def organize_dist() -> None:
    print("Organizando arquivos de distribuição…")

    # readme alongside the exe
    if os.path.exists("leiame.txt"):
        shutil.copy("leiame.txt", GAME_DIR)
    else:
        print("  Aviso: leiame.txt não encontrado, será ignorado.")

    # sounds/ sits alongside lib/, not inside it
    shutil.copytree("sounds", os.path.join(GAME_DIR, "sounds"), ignore=_IGNORE, dirs_exist_ok=True)
    print("  Copiado: sounds  →  sounds/")

    lib_dir = os.path.join(GAME_DIR, "lib")
    os.makedirs(lib_dir, exist_ok=True)

    for src, dst_name in [
        ("accessible_output2", "accessible_output2"),
        ("sound_lib",          "sound_lib"),
    ]:
        dst = os.path.join(lib_dir, dst_name)
        shutil.copytree(src, dst, ignore=_IGNORE, dirs_exist_ok=True)
        print(f"  Copiado: {src}  →  lib/{dst_name}/")


def create_zip() -> None:
    zip_path = os.path.join(DIST_DIR, f"{GAME_NAME}.zip")
    print(f"Criando {zip_path}…")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, _dirs, files in os.walk(GAME_DIR):
            for fname in files:
                full    = os.path.join(root, fname)
                arcname = os.path.relpath(full, DIST_DIR)   # path inside zip
                zf.write(full, arcname)
    size_mb = os.path.getsize(zip_path) / 1_048_576
    print(f"  Zip criado: {zip_path}  ({size_mb:.1f} MB)")


def cleanup() -> None:
    for path in (f"{GAME_NAME}.spec", "build"):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Start fresh
    if os.path.isdir(GAME_DIR):
        print(f"Limpando build anterior em {GAME_DIR}…")
        shutil.rmtree(GAME_DIR)

    try:
        run_pyinstaller()
        organize_dist()
        create_zip()
        print(f"\n✓ Build concluído com sucesso!\n  Pasta: {GAME_DIR}\n  Zip:   {os.path.join(DIST_DIR, GAME_NAME + '.zip')}")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ PyInstaller falhou com código {e.returncode}.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        raise
    finally:
        cleanup()


if __name__ == "__main__":
    main()
