from enum import Enum
from typing import Optional, Callable
from datetime import datetime
from dataclasses import dataclass


class TimerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class PomodoroPhase(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass
class TimerConfig:
    work_duration_seconds: int = 25 * 60
    short_break_seconds: int = 5 * 60
    long_break_seconds: int = 15 * 60
    pomodoros_until_long_break: int = 4
    auto_start_break: bool = False
    auto_start_work: bool = False


class PomodoroTimer:
    def __init__(self, config: Optional[TimerConfig] = None):
        self.config = config or TimerConfig()
        self._state = TimerState.IDLE
        self._phase = PomodoroPhase.WORK
        self._remaining_seconds = self.config.work_duration_seconds
        self._elapsed_seconds = 0
        self._pomodoros_completed = 0
        self._current_task_id: Optional[int] = None
        self._session_start_time: Optional[datetime] = None
        self._on_tick_callback: Optional[Callable[[int, int], None]] = None
        self._on_state_change_callback: Optional[Callable[[TimerState], None]] = None
        self._on_phase_complete_callback: Optional[Callable[[PomodoroPhase], None]] = None
        self._on_phase_change_callback: Optional[Callable[[PomodoroPhase], None]] = None

    @property
    def state(self) -> TimerState:
        return self._state

    @property
    def phase(self) -> PomodoroPhase:
        return self._phase

    @property
    def remaining_seconds(self) -> int:
        return self._remaining_seconds

    @property
    def elapsed_seconds(self) -> int:
        return self._elapsed_seconds

    @property
    def pomodoros_completed(self) -> int:
        return self._pomodoros_completed

    @property
    def current_task_id(self) -> Optional[int]:
        return self._current_task_id

    @property
    def session_start_time(self) -> Optional[datetime]:
        return self._session_start_time

    @property
    def total_duration_seconds(self) -> int:
        if self._phase == PomodoroPhase.WORK:
            return self.config.work_duration_seconds
        elif self._phase == PomodoroPhase.SHORT_BREAK:
            return self.config.short_break_seconds
        else:
            return self.config.long_break_seconds

    def set_callbacks(self, on_tick: Optional[Callable[[int, int], None]] = None,
                      on_state_change: Optional[Callable[[TimerState], None]] = None,
                      on_phase_complete: Optional[Callable[[PomodoroPhase], None]] = None,
                      on_phase_change: Optional[Callable[[PomodoroPhase], None]] = None):
        self._on_tick_callback = on_tick
        self._on_state_change_callback = on_state_change
        self._on_phase_complete_callback = on_phase_complete
        self._on_phase_change_callback = on_phase_change

    def set_current_task(self, task_id: Optional[int]):
        self._current_task_id = task_id

    def start(self, task_id: Optional[int] = None):
        if self._state == TimerState.IDLE:
            if task_id is not None:
                self._current_task_id = task_id
            self._session_start_time = datetime.now()
            self._set_state(TimerState.RUNNING)
        elif self._state == TimerState.PAUSED:
            self._set_state(TimerState.RUNNING)

    def pause(self):
        if self._state == TimerState.RUNNING:
            self._set_state(TimerState.PAUSED)

    def resume(self):
        if self._state == TimerState.PAUSED:
            self._set_state(TimerState.RUNNING)

    def skip(self):
        self._complete_phase(skipped=True)

    def reset(self):
        self._state = TimerState.IDLE
        self._remaining_seconds = self._get_phase_duration()
        self._elapsed_seconds = 0
        self._session_start_time = None
        self._set_state(TimerState.IDLE)

    def tick(self):
        if self._state != TimerState.RUNNING:
            return

        self._remaining_seconds -= 1
        self._elapsed_seconds += 1

        if self._on_tick_callback:
            self._on_tick_callback(self._remaining_seconds, self._elapsed_seconds)

        if self._remaining_seconds <= 0:
            self._complete_phase()

    def _complete_phase(self, skipped: bool = False):
        # 计算是否真正完成（时间耗尽）还是跳过
        is_completed = not skipped and self._remaining_seconds <= 0

        if self._on_phase_complete_callback:
            self._on_phase_complete_callback(self._phase, is_completed)

        if self._phase == PomodoroPhase.WORK and not skipped:
            self._pomodoros_completed += 1

        self._advance_phase()
        self.reset()

        if self.config.auto_start_break and self._phase in (PomodoroPhase.SHORT_BREAK, PomodoroPhase.LONG_BREAK):
            self.start()
        elif self.config.auto_start_work and self._phase == PomodoroPhase.WORK:
            self.start()

    def _advance_phase(self):
        if self._phase == PomodoroPhase.WORK:
            if self._pomodoros_completed > 0 and self._pomodoros_completed % self.config.pomodoros_until_long_break == 0:
                self._phase = PomodoroPhase.LONG_BREAK
            else:
                self._phase = PomodoroPhase.SHORT_BREAK
        else:
            self._phase = PomodoroPhase.WORK

        self._remaining_seconds = self._get_phase_duration()
        self._elapsed_seconds = 0

        if self._on_phase_change_callback:
            self._on_phase_change_callback(self._phase)

    def _get_phase_duration(self) -> int:
        if self._phase == PomodoroPhase.WORK:
            return self.config.work_duration_seconds
        elif self._phase == PomodoroPhase.SHORT_BREAK:
            return self.config.short_break_seconds
        else:
            return self.config.long_break_seconds

    def _set_state(self, new_state: TimerState):
        old_state = self._state
        self._state = new_state
        if old_state != new_state and self._on_state_change_callback:
            self._on_state_change_callback(new_state)

    def update_config(self, config: TimerConfig):
        self.config = config
        if self._state == TimerState.IDLE:
            self._remaining_seconds = self._get_phase_duration()

    def get_progress_percent(self) -> float:
        total = self.total_duration_seconds
        if total == 0:
            return 0.0
        return (self._elapsed_seconds / total) * 100

    def format_time(self, seconds: Optional[int] = None) -> str:
        if seconds is None:
            seconds = self._remaining_seconds
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
