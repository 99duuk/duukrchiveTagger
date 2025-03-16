# """로깅 관련 유틸"""
import sys
import time

class ProgressLogger:
    """ brew install과 같은 프로그레스 바 스타일 로깅 클래스  """

    @staticmethod
    def start_section(message):
        """ 로깅 헤더 """
        print(f"\n==> {message}", flush=True)

    @staticmethod
    def log_step(message, cmd=False):
        prefix = "⌘ " if cmd else "   "
        print(f"{prefix}{message}", flush=True)

    @staticmethod
    def print_progress(task_id, current, total, prefix="==> Processing"):
        if total == 0:
            return

        progress = (current / total) * 100
        bar_length = 30     # fixed length of progress bar
        filled_length = int(bar_length * current // total)
        bar = "#" * filled_length + " " * (bar_length - filled_length)

        sys.stdout.write(f"\r{prefix} {task_id}... {bar} {progress:.1f}%")
        sys.stdout.flush()

        if current == total:
            print()     # Move to next line when done

    @staticmethod
    def log_completion(message):
        print(f"✓ {message}", flush=True)


    @staticmethod
    def log_error(message):
        print(f"✗ Error: {message}", flush=True)


# Example usage (for testing)
if __name__ == "__main__":
    ProgressLogger.start_section("Installing dependencies")
    ProgressLogger.log_step("Pouring icu4c-69.1", cmd=True)
    for i in range(101):
        ProgressLogger.print_progress("package1", i, 100)
        time.sleep(0.01)
    ProgressLogger.log_completion("Installation complete")

