from aiohttp import web
from articles_parser import get_analytics_for_articles


MAX_LIMIT_URLS = 10


async def handle(request):
    urls = request.query.get('urls')
    if not urls:
        return web.json_response({})

    formatted_urls = urls.split(',')
    if len(formatted_urls) > MAX_LIMIT_URLS:
        return web.HTTPBadRequest(
            text=f'Too many urls in request, '
                 f'should be {MAX_LIMIT_URLS} or less'
        )
    analytics_for_articles = await get_analytics_for_articles(formatted_urls)
    return web.json_response(analytics_for_articles)


app = web.Application()
app.add_routes([web.get('/', handle)])


if __name__ == '__main__':
    web.run_app(app)
