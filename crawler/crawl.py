import os
import json
import asyncio
import re
from typing import List
from urllib import parse
from bs4 import BeautifulSoup
from aiohttp import ClientSession


def check_case(text: str) -> str:
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    lst = text.split()
    for i in range(len(lst)):
        word = lst[i]
        if word.lower() in ["in", "of", "on", "and", "for"]:
            word = word.lower()
        else:
            if len(word) == 1:
                word = word
            else:
                word = f"{word[0].upper()}{word[1:]}"
        lst[i] = word
    return " ".join(lst)


headers = {
    "User-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
                  " (KHTML, like Gecko) CriOS/97.0.4692.84 Mobile/15E148 Safari/604.1"
}
proxy = os.getenv("crawler_proxy")
articles = []
users = []
scholar_users = []
scholar_article_titles = []
tags = set()


async def scrape_user_info(url: str, session: ClientSession, order: int) -> dict:
    url = f"https://scholar.google.com{url}"
    response = await session.get(url, headers=headers, proxy=proxy)
    soup = BeautifulSoup(await response.text(), "lxml")
    name = soup.select_one('#gsc_prf_in').text
    headline = soup.select_one('#gsc_prf_in+ .gsc_prf_il').text
    avatar = soup.select_one("#gsc_prf_pup-img")["src"]
    if avatar and not avatar.startswith("http"):
        avatar = None
    user_mail_homepage = soup.select_one('#gsc_prf_ivh')
    try:
        email_domain = re.search(
            "Verified email at (?P<domain>([a-z.\-]+\.[a-z]+)).*", user_mail_homepage.text
        ).group("domain")
    except:
        email_domain = None

    try:
        website = user_mail_homepage.select_one("a")["href"]
    except:
        website = None

    user_tags = []
    for tag in soup.select_one('#gsc_prf_int').select("a"):
        tag_text = check_case(tag.text)
        tags.add(tag_text)
        user_tags.append(tag_text)

    user_info = {
        "full_name": name,
        "headline": headline,
        "id": parse.parse_qs(parse.urlparse(url).query)['user'][0]
    }
    if email_domain:
        user_info.update({"email_domain": email_domain})
    if website:
        user_info.update({"website": website})
    if user_tags:
        user_info.update({"tags": user_tags})
    if avatar:
        user_info.update({"avatar": avatar})

    if user_info["id"] not in scholar_users:
        scholar_users.append(user_info["id"])
        users.append(user_info)
    return {"id": user_info["id"], "full_name": user_info["full_name"], "order": order}


async def scrape_search_result_page(coroutine, session: ClientSession, scrape_cited_by=True) -> List[dict]:
    page_articles = []
    response = await coroutine
    soup = BeautifulSoup(
        await response.text(),
        "lxml",
    )

    for res in soup.select(".gs_r.gs_or"):
        try:
            title = res.select_one(".gs_rt").select_one("a").text
        except AttributeError:
            title = res.select_one(".gs_rt").text
        if title in scholar_article_titles:
            continue
        print("adding document", f'"{title}"')
        scholar_article_titles.append(title)
        try:
            pdf = res.select_one(".gs_or_ggsm a")["href"]
        except TypeError:
            pdf = None
        publication_info = res.select_one(".gs_a")
        try:
            year = re.search(r'\d+', publication_info.text).group()
        except:
            year = None

        snippet = res.select_one(".gs_rs").text
        author_tasks = []
        author_order = 1
        for link in publication_info.select("a"):
            author_tasks.append(scrape_user_info(link["href"], session, order=author_order))
            author_order += 1
        try:
            authors = await asyncio.gather(*author_tasks)
        except AttributeError:
            continue
        citations = []
        if scrape_cited_by:
            citations_coroutine = session.get(
                f'https://scholar.google.com{res.select_one("#gs_res_ccl_mid .gs_nph+ a")["href"]}',
                headers=headers,
                proxy=proxy,
            )
            citations_result = await scrape_search_result_page(citations_coroutine, session, scrape_cited_by=False)
            for citation in citations_result:
                citations.append(citation["id"])

        publication = {"title": publication_info.text.split()[-1]}
        if year:
            publication.update({"year": year})

        document = {
            "id": len(articles) + 1,
            "title": title,
            "publication": publication,
            "snippet": snippet,
            "authors": authors,
        }
        if pdf:
            document.update({"file": pdf})
        if citations:
            document.update({"citations": citations})
        page_articles.append(document)
        articles.append(document)

    return page_articles


async def crawl_scholar():
    tasks = []
    async with ClientSession() as session:
        for query in [
            "web mining", "nosql database", "data mining", "relational database", "elasticsearch", "cloud computing",
            "distributed systems", "compilers", "deep learning", "knowledge discovery", "data analysis", "hpc",
            "autoscaling", "docker container", "scheduling", "lstm", "graph theory", "queueing theory", "sql"
        ]:
            params = {
                "q": query,
                "hl": "en",
            }
            coroutine = session.get(
                "https://scholar.google.com/scholar",
                headers=headers,
                params=params,
                proxy=proxy,
            )
            tasks.append(scrape_search_result_page(coroutine, session))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(crawl_scholar())
    print("length of articles", len(articles))
    print("length of users", len(users))
    print("length of tags", len(tags))
    articles = json.dumps(articles, indent=2, ensure_ascii=False)
    users = json.dumps(users, indent=2, ensure_ascii=False)
    tags = list(map(lambda t: {"name": t}, list(tags)))
    tags = json.dumps(tags, indent=2, ensure_ascii=False)
    directory = os.path.dirname(__file__)
    with open(f"{directory}/papers.json", "w") as out_file:
        out_file.write(articles)

    with open(f"{directory}/authors.json", "w") as out_file:
        out_file.write(users)

    with open(f"{directory}/tags.json", "w") as out_file:
        out_file.write(tags)
