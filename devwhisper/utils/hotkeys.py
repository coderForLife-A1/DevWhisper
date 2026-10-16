"""Thread-safe global hotkey manager using pynput and PySide6 signals."""
from typing import Dict, Callable
from pynput import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyBridge(QObject):
    """Bridge emitting Qt signals from pynput's background OS hook thread."""
    triggered = Signal(str)


class GlobalHotkeyManager:
    """Manages system-wide hotkeys."""

    def __init__(self, hotkey_actions: Dict[str, Callable[[], None]]):
        self.bridge = HotkeyBridge()
        self._actions = {}
        self._callbacks = hotkey_actions

        for hotkey_str in hotkey_actions.keys():
            self._actions[hotkey_str] = lambda name=hotkey_str: self.bridge.triggered.emit(name)

        self.bridge.triggered.connect(self._dispatch)
        self._listener = None

    def _dispatch(self, name: str):
        cb = self._callbacks.get(name)
        if cb:
            cb()

    def start(self):
        if self._listener is None:
            try:
                self._listener = keyboard.GlobalHotKeys(self._actions)
                self._listener.start()
            except Exception as e:
                print(f"[Hotkeys] Warning: could not start global hotkey listener: {e}")

    def stop(self):
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

