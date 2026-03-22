import pytest
from datetime import datetime

from src.timer.pomodoro_timer import PomodoroTimer, TimerState, PomodoroPhase, TimerConfig


class TestPomodoroTimer:
    @pytest.fixture
    def timer(self):
        config = TimerConfig(
            work_duration_seconds=5,
            short_break_seconds=2,
            long_break_seconds=3,
            pomodoros_until_long_break=2,
        )
        return PomodoroTimer(config)

    def test_initial_state(self, timer):
        assert timer.state == TimerState.IDLE
        assert timer.phase == PomodoroPhase.WORK
        assert timer.remaining_seconds == 5

    def test_start(self, timer):
        timer.start()

        assert timer.state == TimerState.RUNNING
        assert timer.session_start_time is not None

    def test_pause(self, timer):
        timer.start()
        timer.pause()

        assert timer.state == TimerState.PAUSED

    def test_resume(self, timer):
        timer.start()
        timer.pause()
        timer.resume()

        assert timer.state == TimerState.RUNNING

    def test_tick(self, timer):
        timer.start()
        initial_remaining = timer.remaining_seconds
        timer.tick()

        assert timer.remaining_seconds == initial_remaining - 1
        assert timer.elapsed_seconds == 1

    def test_tick_does_not_decrement_when_paused(self, timer):
        timer.start()
        timer.pause()
        initial_remaining = timer.remaining_seconds
        timer.tick()

        assert timer.remaining_seconds == initial_remaining

    def test_tick_does_not_decrement_when_idle(self, timer):
        initial_remaining = timer.remaining_seconds
        timer.tick()

        assert timer.remaining_seconds == initial_remaining

    def test_phase_completion_transitions_to_short_break(self, timer):
        timer.start()
        for _ in range(5):
            timer.tick()

        assert timer.phase == PomodoroPhase.SHORT_BREAK
        assert timer.remaining_seconds == 2
        assert timer.pomodoros_completed == 1

    def test_phase_completion_transitions_to_long_break(self, timer):
        timer.config.pomodoros_until_long_break = 1
        timer.start()
        for _ in range(5):
            timer.tick()

        assert timer.phase == PomodoroPhase.LONG_BREAK
        assert timer.remaining_seconds == 3

    def test_skip(self, timer):
        timer.start()
        timer.skip()

        assert timer.phase == PomodoroPhase.SHORT_BREAK
        assert timer.state == TimerState.IDLE

    def test_reset(self, timer):
        timer.start()
        for _ in range(2):
            timer.tick()
        timer.reset()

        assert timer.state == TimerState.IDLE
        assert timer.remaining_seconds == 5
        assert timer.elapsed_seconds == 0

    def test_get_progress_percent(self, timer):
        timer.start()
        timer.tick()

        progress = timer.get_progress_percent()
        assert progress == 20.0

    def test_format_time(self, timer):
        assert timer.format_time(125) == "02:05"
        assert timer.format_time(0) == "00:00"
        assert timer.format_time(3600) == "60:00"

    def test_set_current_task(self, timer):
        timer.set_current_task(42)
        assert timer.current_task_id == 42

    def test_callbacks(self, timer):
        tick_values = []
        state_values = []
        phase_values = []

        timer.set_callbacks(
            on_tick=lambda r, e: tick_values.append((r, e)),
            on_state_change=lambda s: state_values.append(s),
            on_phase_change=lambda p: phase_values.append(p),
        )

        timer.start()
        timer.tick()

        assert len(tick_values) == 1
        assert tick_values[0] == (4, 1)
        assert TimerState.RUNNING in state_values

    def test_update_config(self, timer):
        new_config = TimerConfig(
            work_duration_seconds=30 * 60,
            short_break_seconds=5 * 60,
            long_break_seconds=15 * 60,
        )
        timer.update_config(new_config)

        assert timer.remaining_seconds == 30 * 60

    def test_auto_start_break(self):
        config = TimerConfig(
            work_duration_seconds=2,
            short_break_seconds=1,
            auto_start_break=True,
        )
        timer = PomodoroTimer(config)
        timer.start()
        for _ in range(2):
            timer.tick()

        assert timer.phase == PomodoroPhase.SHORT_BREAK
        assert timer.state == TimerState.RUNNING

    def test_pomodoro_count_increments_only_on_work_completion(self, timer):
        timer.start()
        for _ in range(5):
            timer.tick()

        assert timer.pomodoros_completed == 1

        for _ in range(2):
            timer.tick()

        assert timer.pomodoros_completed == 1

    def test_elapsed_seconds_tracks_correctly(self, timer):
        timer.start()
        for i in range(3):
            timer.tick()
            assert timer.elapsed_seconds == i + 1
