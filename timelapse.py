import ctypes
import msvcrt
import time
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path

import mss
import mss.tools


DEFAULT_OUTPUT_DIR = "timelapse_frames"
MONITORINFOF_PRIMARY = 1
PAUSE_KEY = "p"
KEYBOARD_POLL_INTERVAL_SECONDS = 0.1


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


@dataclass(frozen=True)
class ScreenRegion:
    left: int
    top: int
    width: int
    height: int

    @classmethod
    def from_mss_monitor(cls, monitor: dict[str, int]) -> "ScreenRegion":
        return cls(
            left=monitor["left"],
            top=monitor["top"],
            width=monitor["width"],
            height=monitor["height"],
        )

    @property
    def key(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.width, self.height)

    def as_mss_monitor(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }

    def describe(self) -> str:
        return f"{self.width}x{self.height} em ({self.left}, {self.top})"


@dataclass(frozen=True)
class MonitorOption:
    index: int
    region: ScreenRegion
    is_primary: bool = False

    def describe(self) -> str:
        suffix = " (principal)" if self.is_primary else ""
        return f"{self.index}: {self.region.describe()}{suffix}"


def read_pressed_key() -> str | None:
    if not msvcrt.kbhit():
        return None

    key = msvcrt.getwch()
    if key in ("\x00", "\xe0") and msvcrt.kbhit():
        msvcrt.getwch()
        return None

    return key.lower()


def wait_with_pause_control(interval_seconds: float) -> bool:
    deadline = time.monotonic() + interval_seconds

    while time.monotonic() < deadline:
        if read_pressed_key() == PAUSE_KEY:
            return True

        time.sleep(KEYBOARD_POLL_INTERVAL_SECONDS)

    return False


def get_primary_monitor_key() -> tuple[int, int, int, int] | None:
    user32 = ctypes.windll.user32
    primary_monitor = None

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM,
    )

    def callback(hmonitor, _hdc, _rect, _lparam):
        nonlocal primary_monitor

        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        is_primary = user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)) and (
            info.dwFlags & MONITORINFOF_PRIMARY
        )
        if is_primary:
            primary_monitor = (
                info.rcMonitor.left,
                info.rcMonitor.top,
                info.rcMonitor.right - info.rcMonitor.left,
                info.rcMonitor.bottom - info.rcMonitor.top,
            )
            return 0

        return 1

    user32.EnumDisplayMonitors(0, 0, monitor_enum_proc(callback), 0)
    return primary_monitor


def list_monitors(sct: mss.mss) -> list[MonitorOption]:
    primary_key = get_primary_monitor_key()
    monitors: list[MonitorOption] = []

    for index, monitor in enumerate(sct.monitors[1:], start=1):
        region = ScreenRegion.from_mss_monitor(monitor)
        monitors.append(
            MonitorOption(
                index=index,
                region=region,
                is_primary=region.key == primary_key,
            )
        )

    if monitors and not any(monitor.is_primary for monitor in monitors):
        monitors[0] = MonitorOption(
            index=monitors[0].index,
            region=monitors[0].region,
            is_primary=True,
        )

    return monitors


def require_primary_monitor(monitors: list[MonitorOption]) -> ScreenRegion:
    if not monitors:
        raise RuntimeError("Nenhum monitor individual foi encontrado.")

    for monitor in monitors:
        if monitor.is_primary:
            return monitor.region

    raise RuntimeError("Nao foi possivel determinar o monitor principal.")


def select_monitor_interactively(monitors: list[MonitorOption]) -> ScreenRegion:
    default_monitor = require_primary_monitor(monitors)

    print("\nMonitores disponiveis:")
    for monitor in monitors:
        print(monitor.describe())

    while True:
        choice = input("Selecione o monitor para gravar [Enter = principal]: ").strip()
        if not choice:
            return default_monitor

        if choice.isdigit():
            selected_index = int(choice)
            for monitor in monitors:
                if monitor.index == selected_index:
                    return monitor.region

        print("Monitor invalido. Digite um numero da lista ou pressione Enter para usar o principal.")


def prompt_capture_interval() -> float:
    while True:
        raw_value = input("Digite o intervalo entre capturas, em segundos: ").strip()
        try:
            interval_seconds = float(raw_value)
        except ValueError:
            print("Intervalo invalido. Digite um numero maior que zero.")
            continue

        if interval_seconds <= 0:
            print("Intervalo invalido. Digite um numero maior que zero.")
            continue

        return interval_seconds


def prompt_output_dir() -> str:
    output_dir = input(f"Digite o nome da pasta de saída [{DEFAULT_OUTPUT_DIR}]: ").strip()
    return output_dir or DEFAULT_OUTPUT_DIR


def capture_screen(
    interval_seconds: float,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    selected_monitor: ScreenRegion | None = None,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with mss.mss() as sct:
        monitor = selected_monitor
        if monitor is None:
            monitor = require_primary_monitor(list_monitors(sct))

        print(f"Salvando prints em: {output_path.resolve()}")
        print(f"Intervalo: {interval_seconds} segundo(s)")
        print(f"Monitor: {monitor.describe()}")
        print("Pressione P para pausar/retomar.")
        print("Pressione Ctrl + C para parar.\n")

        frame_counter = 1
        paused = False

        try:
            while True:
                if paused:
                    if read_pressed_key() == PAUSE_KEY:
                        paused = False
                        print("Captura retomada.")
                    else:
                        time.sleep(KEYBOARD_POLL_INTERVAL_SECONDS)
                    continue

                output_file = output_path / f"{frame_counter:06d}.png"
                screenshot = sct.grab(monitor.as_mss_monitor())
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(output_file))

                print(f"[{frame_counter:06d}] Capturado: {output_file.name}")
                frame_counter += 1

                if wait_with_pause_control(interval_seconds):
                    paused = True
                    print("Captura pausada. Pressione P para retomar.")

        except KeyboardInterrupt:
            print("\nCaptura encerrada pelo usuario.")


def main() -> int:
    interval_seconds = prompt_capture_interval()
    output_dir = prompt_output_dir()

    with mss.mss() as sct:
        selected_monitor = select_monitor_interactively(list_monitors(sct))

    capture_screen(
        interval_seconds=interval_seconds,
        output_dir=output_dir,
        selected_monitor=selected_monitor,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
