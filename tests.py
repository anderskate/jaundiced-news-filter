import pytest
from articles_parser import process_article, ProcessingStatus


@pytest.mark.asyncio
async def test_process_article_with_incorrect_page():
    """Test process article with incorrect page."""
    article_url = 'https://inosmi.ru/military/20211107/incorrect_page.html'
    articles_results = []
    await process_article(article_url, articles_results)

    article_info = articles_results[0]
    assert len(articles_results) == 1
    assert article_info.status == ProcessingStatus.FETCH_ERROR.value


@pytest.mark.asyncio
async def test_process_article_with_diferent_resource():
    """Test process article from different resource."""
    article_url = 'https://lenta.ru/brief/2021/08/26/afg_terror/'
    articles_results = []
    await process_article(article_url, articles_results)

    article_info = articles_results[0]
    assert len(articles_results) == 1
    assert article_info.status == ProcessingStatus.PARSING_ERROR.value


@pytest.mark.asyncio
async def test_process_article_with_parse_timeout():
    """Test process article with a timeout when parsing."""
    article_url = 'https://inosmi.ru/politic/20211014/250703064.html'
    articles_results = []
    await process_article(article_url, articles_results, parsing_timeout=0.3)

    article_info = articles_results[0]
    assert len(articles_results) == 1
    assert article_info.status == ProcessingStatus.TIMEOUT.value
