import argparse
import requests
import sys
import time
from typing import Sequence

import logging
logger = logging.getLogger("speedtest")

DEFAULT_REQUESTS = 10
DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_READ_TIMEOUT = 30
MAX_REQUEST_DURATION = 10
CHUNK_SIZE = 64 * 1024
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ""AppleWebKit/537.36 (KHTML, like Gecko) ""Chrome/128.0.6613.120 Safari/537.36"

# Минимальный размер ресурса для осмысленного замера
MIN_RESOURCE_BYTES = 10 * 1024 * 1024  # 10 MiB

BITS_PER_BYTE = 8
BITS_PER_MEGABIT = 1_000_000


class ResourceTooSmallError(Exception):
    """Ресурс меньше минимального размера"""


def measure_once(session: requests.Session, url: str, timeout: tuple[float, float], max_duration: float,) -> tuple[int, float, bool]:
    """Выполняет один запрос и замеряет время"""

    truncated = False

    start = time.perf_counter()
    with session.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()

        bytes_downloaded = 0
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            bytes_downloaded += len(chunk)
            if time.perf_counter() - start >= max_duration:
                truncated = True
                break

        total_time = time.perf_counter() - start

    return bytes_downloaded, total_time, truncated


def run_benchmark(url: str, count: int, connect_timeout: float, read_timeout: float, max_duration: float,) -> list[tuple[int, float, bool]]:
    """
    Выплняет несколько последовательных запросов.
    Первый запрос — прогрев соединения (DNS + TCP + TLS + slow start).
    Его результат возвращается, но в статистике не учитывается.
    """

    results: list[tuple[int, float, bool]] = []

    timeout = (connect_timeout, read_timeout)
    headers = {"User-Agent": USER_AGENT}

    with requests.Session() as session:
        session.headers.update(headers)

        for i in range(1, count + 1):
            if i == 1:
                logger.info("[%2d/%d] GET %s (прогрев, не учитывается)", i, count, url)
            else:
                logger.info("[%2d/%d] GET %s", i, count, url)

            bytes_downloaded, total_time, truncated = measure_once(
                session, url, timeout, max_duration
            )
            results.append((bytes_downloaded, total_time, truncated))

            speed_mbps = (
                bytes_downloaded * BITS_PER_BYTE / total_time / BITS_PER_MEGABIT
            )
            note = " (прервано по лимиту времени)" if truncated else ""
            logger.info(
                "        %s за %.3f с (%.2f Mbps)%s",
                format_bytes(bytes_downloaded),
                total_time,
                speed_mbps,
                note,
            )

            # проверка на размер ресурса
            if i == 1 and not truncated and bytes_downloaded < MIN_RESOURCE_BYTES:
                raise ResourceTooSmallError(
                    f"Ресурс слишком мал ({format_bytes(bytes_downloaded)}). "
                    f"Для осмысленного замера нужен ресурс от "
                    f"{format_bytes(MIN_RESOURCE_BYTES)} и выше."
                )

    return results


def format_bytes(n: int) -> str:
    """Человекочитаемый размер в байтах"""
    if n >= 1024 ** 3:
        return f"{n / 1024 ** 3:.2f} GiB"
    if n >= 1024 ** 2:
        return f"{n / 1024 ** 2:.2f} MiB"
    if n >= 1024:
        return f"{n / 1024:.2f} KiB"
    return f"{n} B"


def format_mbps(mbps: float) -> str:
    return f"{mbps:.2f} Mbps"


def print_report(url: str, results: Sequence[tuple[int, float, bool]]) -> None:
    warmup, *measured = results
    if not measured:
        logger.error("Недостаточно замеров для статистики")
        return

    all_bytes = [r[0] for r in measured]
    all_times = [r[1] for r in measured]

    total_bytes = sum(all_bytes)
    total_time = sum(all_times)

    # скорость — отношение суммы байт к сумме времени
    avg_speed_mbps = total_bytes * BITS_PER_BYTE / total_time / BITS_PER_MEGABIT
    avg_time = total_time / len(measured)

    logger.info("")
    logger.info("=" * 68)
    logger.info("URL:              %s", url)
    logger.info("Среднее время:    %.3f с", avg_time)
    logger.info("Средняя скорость: %s", format_mbps(avg_speed_mbps))
    logger.info("=" * 68)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Замер скорости скачивания HTTP-ресурса.",
    )
    parser.add_argument(
        "url",
        help="URL ресурса для скачивания",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    args = parse_args(argv)

    try:
        results = run_benchmark(
            args.url,
            DEFAULT_REQUESTS,
            DEFAULT_CONNECT_TIMEOUT,
            DEFAULT_READ_TIMEOUT,
            MAX_REQUEST_DURATION,
        )
    except KeyboardInterrupt:
        logger.error("Прервано пользователем")
        return 130
    except ResourceTooSmallError as exc:
        logger.error("%s", exc)
        return 1
    except requests.exceptions.RequestException as exc:
        logger.error("Запрос не удался: %s", exc)
        return 1

    print_report(args.url, results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
