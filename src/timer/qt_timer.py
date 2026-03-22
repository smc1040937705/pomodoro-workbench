from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from typing import Optional
from datetime import datetime

from .pomodoro_timer import PomodoroTimer, TimerState, PomodoroPhase, TimerConfig


class QtPomodoroTimer(QObject):
    tick = pyqtSignal(int, int)
    state_changed = pyqtSignal(object)
    phase_completed = pyqtSignal(object, datetime, datetime, bool)
    phase_changed = pyqtSignal(object)
    pomodoro_completed = pyqtSignal(int)

    def __init__(self, config: Optional[TimerConfig] = None, parent=None):
        super().__init__(parent)
        self._timer = PomodoroTimer(config)
        self._qtimer = QTimer(self)
        self._qtimer.timeout.connect(self._on_qtimer_tick)
        self._timer.set_callbacks(
            on_tick=self._on_timer_tick,
            on_state_change=self._on_state_change,
            on_phase_complete=self._on_phase_complete,
            on_phase_change=self._on_phase_change
        )

    @property
    def state(self) -> TimerState:
        return self._timer.state

    @property
    def phase(self) -> PomodoroPhase:
        return self._timer.phase

    @property
    def remaining_seconds(self) -> int:
        return self._timer.remaining_seconds

    @property
    def elapsed_seconds(self) -> int:
        return self._timer.elapsed_seconds

    @property
    def pomodoros_completed(self) -> int:
        return self._timer.pomodoros_completed

    @property
    def current_task_id(self) -> Optional[int]:
        return self._timer.current_task_id

    @property
    def session_start_time(self) -> Optional[datetime]:
        return self._timer.session_start_time

    @property
    def total_duration_seconds(self) -> int:
        return self._timer.total_duration_seconds

    @property
    def config(self) -> TimerConfig:
        return self._timer.config

    def set_current_task(self, task_id: Optional[int]):
        self._timer.set_current_task(task_id)

    def start(self, task_id: Optional[int] = None):
        self._timer.start(task_id)
        self._qtimer.start(1000)

    def pause(self):
        self._timer.pause()
        self._qtimer.stop()

    def resume(self):
        self._timer.resume()
        self._qtimer.start(1000)

    def skip(self):
        self._timer.skip()

    def reset(self):
        self._timer.reset()
        self._qtimer.stop()

    def update_config(self, config: TimerConfig):
        self._timer.update_config(config)

    def get_progress_percent(self) -> float:
        return self._timer.get_progress_percent()

    def format_time(self, seconds: Optional[int] = None) -> str:
        return self._timer.format_time(seconds)

    def _on_qtimer_tick(self):
        self._timer.tick()

    def _on_timer_tick(self, remaining: int, elapsed: int):
        self.tick.emit(remaining, elapsed)

    def _on_state_change(self, state: TimerState):
        if state == TimerState.IDLE or state == TimerState.PAUSED:
            self._qtimer.stop()
        elif state == TimerState.RUNNING:
            if not self._qtimer.isActive():
                self._qtimer.start(1000)
        self.state_changed.emit(state)

    def _on_phase_complete(self, phase: PomodoroPhase):
        start_time = self._timer.session_start_time
        end_time = datetime.now()
        is_completed = self._timer.remaining_seconds <= 0
        self.phase_completed.emit(phase, start_time or end_time, end_time, is_completed)
        if phase == PomodoroPhase.WORK and is_completed:
            self.pomodoro_completed.emit(self._timer.pomodoros_completed)

    def _on_phase_change(self, phase: PomodoroPhase):
        self.phase_changed.emit(phase)
