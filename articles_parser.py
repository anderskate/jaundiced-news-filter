import time
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, List
from contextlib import contextmanager

import aiohttp
import asyncio
import pymorphy2
import aiofiles
from anyio import create_task_group
from async_timeout import timeout
from loguru import logger

import adapters.exceptions
from adapters.inosmi_ru import sanitize
from text_tools import split_by_words, calculate_jaundice_rate


DEFAULT_TIMEOUT = 5.0


class ProcessingStatus(Enum):
    """Providing statuses when parsing an articles."""
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


@dataclass
class ArticleInfo:
    """Represent information about article with rating."""
    url: str
    status: str
    rating: Optional[float] = None
    words_count: Optional[int] = None


@contextmanager
def article_parse_counter():
    """Context manager for counting parsing process."""
    start = time.monotonic()
    logger.info('Start analyze article.')
    try:
        yield
    finally:
        end = time.monotonic()
        logger.info(f'Article analysis completed in: {end - start} sec.')


TEST_ARTICLES = [
    'https://dvmn.org/media/',
    'https://inosmi.ru/politic/20211105/250848301.html',
    'https://inosmi.ru/politic/20211014/250703064.html',
    'https://inosmi.ru/economic/20211105/250848061.html',
    'https://inosmi.ru/social/20211105/250847851.html',
    'https://inosmi.ru/social/20211105/250838815.html',
]


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def get_charged_words(filepath: str):
    """Get charged words from specific file."""
    async with aiofiles.open(filepath, mode='r') as f:
        charged_words = []
        async for line in f:
            charged_words.append(line.strip())
    return charged_words


async def process_article(
    article_url: str, articles_results: list,
    parsing_timeout: float = DEFAULT_TIMEOUT
) -> None:
    """Process article and get rating by words."""
    async with aiohttp.ClientSession() as session:
        try:
            async with timeout(parsing_timeout):
                html = await fetch(session, article_url)
        except aiohttp.ClientResponseError:
            articles_results.append(
                ArticleInfo(
                    url=article_url,
                    status=ProcessingStatus.FETCH_ERROR.value,
                )
            )
            return
        except asyncio.exceptions.TimeoutError:
            articles_results.append(
                ArticleInfo(
                    url=article_url,
                    status=ProcessingStatus.TIMEOUT.value,
                )
            )
            return

        try:
            clean_text = sanitize(html)
        except adapters.exceptions.ArticleNotFound:
            articles_results.append(
                ArticleInfo(
                    url=article_url,
                    status=ProcessingStatus.PARSING_ERROR.value,
                )
            )
            return

        morph = pymorphy2.MorphAnalyzer()

        with article_parse_counter():
            try:
                async with timeout(3):
                    article_words = await split_by_words(morph, clean_text)
                    charged_words = await get_charged_words(
                        'charged_dict/negative_words.txt'
                    )
                    rating = calculate_jaundice_rate(
                        article_words, charged_words
                    )
            except asyncio.exceptions.TimeoutError:
                articles_results.append(
                    ArticleInfo(
                        url=article_url,
                        status=ProcessingStatus.TIMEOUT.value,
                    )
                )
                return

        articles_results.append(
            ArticleInfo(
                url=article_url,
                status=ProcessingStatus.OK.value,
                rating=rating, words_count=len(article_words),
            )
        )


async def get_analytics_for_articles(
    articles_urls: [str] = TEST_ARTICLES
) -> [dict]:
    """Get information with analytics for articles."""
    articles_results: List[ArticleInfo] = []
    async with create_task_group() as tg:
        for article_url in articles_urls:
            tg.start_soon(process_article, article_url, articles_results)

    return [asdict(article_data) for article_data in articles_results]


if __name__ == '__main__':
    asyncio.run(get_analytics_for_articles())
