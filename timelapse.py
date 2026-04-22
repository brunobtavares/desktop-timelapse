import msvcrt
import time
from pathlib import Path

import mss


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


def capturar_tela(intervalo_segundos: float, pasta_saida: str = "timelapse_frames"):
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    print(f"Salvando prints em: {pasta.resolve()}")
    print(f"Intervalo: {intervalo_segundos} segundo(s)")
    print("Pressione P para pausar/retomar.")
    print("Pressione Ctrl + C para parar.\n")

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # tela principal
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

    capturar_tela(intervalo_segundos=intervalo, pasta_saida=pasta)
