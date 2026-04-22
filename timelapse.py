import ctypes
import msvcrt
import time
from pathlib import Path
from ctypes import wintypes

import mss


MONITORINFOF_PRIMARY = 1


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def tecla_pressionada() -> str | None:
    if not msvcrt.kbhit():
        return None

    tecla = msvcrt.getwch()
    if tecla in ("\x00", "\xe0") and msvcrt.kbhit():
        msvcrt.getwch()
        return None

    return tecla.lower()


def aguardar_com_controle(intervalo_segundos: float) -> bool:
    fim_espera = time.monotonic() + intervalo_segundos

    while time.monotonic() < fim_espera:
        tecla = tecla_pressionada()
        if tecla == "p":
            return True

        time.sleep(0.1)

    return False


def monitor_para_chave(monitor: dict) -> tuple[int, int, int, int]:
    return (
        monitor["left"],
        monitor["top"],
        monitor["width"],
        monitor["height"],
    )


def obter_chave_monitor_principal() -> tuple[int, int, int, int] | None:
    user32 = ctypes.windll.user32
    monitor_principal = None

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM,
    )

    def callback(hmonitor, _hdc, _rect, _lparam):
        nonlocal monitor_principal

        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)) and info.dwFlags & MONITORINFOF_PRIMARY:
            monitor_principal = (
                info.rcMonitor.left,
                info.rcMonitor.top,
                info.rcMonitor.right - info.rcMonitor.left,
                info.rcMonitor.bottom - info.rcMonitor.top,
            )
            return 0

        return 1

    user32.EnumDisplayMonitors(0, 0, monitor_enum_proc(callback), 0)
    return monitor_principal


def listar_monitores(sct: mss.mss) -> list[dict]:
    monitores = []
    chave_principal = obter_chave_monitor_principal()

    for indice, monitor in enumerate(sct.monitors[1:], start=1):
        monitores.append(
            {
                "indice": indice,
                "dados": monitor,
                "principal": monitor_para_chave(monitor) == chave_principal,
            }
        )

    if monitores and not any(monitor["principal"] for monitor in monitores):
        monitores[0]["principal"] = True

    return monitores


def selecionar_monitor_interativamente(monitores: list[dict]) -> dict:
    if not monitores:
        raise RuntimeError("Nenhum monitor individual foi encontrado.")

    print("\nMonitores disponiveis:")
    for monitor in monitores:
        dados = monitor["dados"]
        principal = " (principal)" if monitor["principal"] else ""
        print(
            f"{monitor['indice']}: {dados['width']}x{dados['height']} "
            f"em ({dados['left']}, {dados['top']}){principal}"
        )

    while True:
        escolha = input("Selecione o monitor para gravar [Enter = principal]: ").strip()
        if not escolha:
            return next(monitor["dados"] for monitor in monitores if monitor["principal"])

        if escolha.isdigit():
            indice_escolhido = int(escolha)
            for monitor in monitores:
                if monitor["indice"] == indice_escolhido:
                    return monitor["dados"]

        print("Monitor invalido. Digite um numero da lista ou pressione Enter para usar o principal.")


def capturar_tela(
    intervalo_segundos: float,
    pasta_saida: str = "timelapse_frames",
    monitor_selecionado: dict | None = None,
):
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    with mss.mss() as sct:
        if monitor_selecionado is None:
            monitores = listar_monitores(sct)
            monitor = next(monitor["dados"] for monitor in monitores if monitor["principal"])
        else:
            monitor = monitor_selecionado

        print(f"Salvando prints em: {pasta.resolve()}")
        print(f"Intervalo: {intervalo_segundos} segundo(s)")
        print(
            "Monitor: "
            f"{monitor['width']}x{monitor['height']} em ({monitor['left']}, {monitor['top']})"
        )
        print("Pressione P para pausar/retomar.")
        print("Pressione Ctrl + C para parar.\n")

        contador = 1
        pausado = False

        try:
            while True:
                if pausado:
                    tecla = tecla_pressionada()
                    if tecla == "p":
                        pausado = False
                        print("Captura retomada.")
                    else:
                        time.sleep(0.1)
                    continue

                nome_arquivo = pasta / f"{contador:06d}.png"

                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=str(nome_arquivo))

                print(f"[{contador:06d}] Capturado: {nome_arquivo.name}")
                contador += 1

                if aguardar_com_controle(intervalo_segundos):
                    pausado = True
                    print("Captura pausada. Pressione P para retomar.")

        except KeyboardInterrupt:
            print("\nCaptura encerrada pelo usuário.")


if __name__ == "__main__":
    intervalo = float(input("Digite o intervalo entre capturas, em segundos: ").strip())
    pasta = input("Digite o nome da pasta de saída [timelapse_frames]: ").strip()

    if not pasta:
        pasta = "timelapse_frames"

    with mss.mss() as sct:
        monitor = selecionar_monitor_interativamente(listar_monitores(sct))

    capturar_tela(intervalo_segundos=intervalo, pasta_saida=pasta, monitor_selecionado=monitor)
