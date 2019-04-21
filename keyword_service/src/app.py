import os
import re

from aiohttp import web
from lxml.html import fromstring
import requests


def concat_words(l: list, res: list) -> tuple:
    """Concat words without permutation."""
    if l:
        res.append(' '.join(l))
        return concat_words(l[:-1], res)
    return None, res


async def gen_keywords(a: list) -> list:
    """Generate keywords from list of words."""
    s = []
    for i in range(len(a)):
        concat_words(a[i:], s)
    return s


async def read_url(url: str) -> list:
    """Get url title keywords."""
    res = requests.get(url)
    tree = fromstring(res.content)
    title = tree.findtext('.//title')
    words = re.findall(r'[\w]+', title)
    return await gen_keywords(words)


async def handler(request):
    data = await request.json()
    res = await read_url(data['url'])
    address_id = request.match_info.get('address_id')
    requests.put(
        os.environ.get('WEB_HOST') + address_id,
        json={'keywords': res},
        headers={'kw-service': os.environ.get('KW_SERVICE_TOKEN')},
    )
    return web.json_response()


app = web.Application()

app.add_routes([
    web.post('/kw/{address_id}', handler),
])

web.run_app(app)
