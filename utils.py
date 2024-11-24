import time


def _input(message: str) -> str:
    while True:
        text = input(message)
        if not text:
            continue

        return text


def _input_get_answer() -> bool:
    while True:
        text = _input('Да или Нет?').lower()
        if text in ['y', '+', 'yes', 'да', 'ага', 'ок', '1']:
            return True

        if text in ['n', '-', 'no', 'нет', 'неа', 'не ок', '0']:
            return False


def custom_print(message: str) -> None:
    print(message)
    time.sleep(1)
