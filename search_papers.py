import os
import requests
from datetime import date

# ---- 설정 ----
KEYWORD = "through glass via"
NUM_PAPERS = 5
RESULTS_DIR = "results"

def search_papers(keyword, rows=5):
    url = "https://api.crossref.org/works"
    params = {
        "query": keyword,
        "rows": rows,
        "sort": "relevance",
        "select": "title,author,DOI,published,container-title,URL",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["message"]["items"]

def format_authors(authors):
    if not authors:
        return "저자 정보 없음"
    names = []
    for a in authors[:3]:
        given = a.get("given", "")
        family = a.get("family", "")
        names.append(f"{given} {family}".strip())
    result = ", ".join(names)
    if len(authors) > 3:
        result += " 외"
    return result

def format_date(item):
    date_parts = item.get("published", {}).get("date-parts", [[None]])[0]
    if date_parts and date_parts[0]:
        return "-".join(str(p) for p in date_parts if p)
    return "날짜 정보 없음"

def build_markdown(items, keyword):
    today = date.today().isoformat()
    lines = [f"# 논문 리포트 - \"{keyword}\"", "", f"생성일: {today}", ""]
    for i, item in enumerate(items, start=1):
        title = item.get("title", ["제목 없음"])[0]
        authors = format_authors(item.get("author", []))
        pub_date = format_date(item)
        journal_list = item.get("container-title", ["출처 미상"])
        journal = journal_list[0] if journal_list else "출처 미상"
        link = item.get("URL", "")
        lines.append(f"## {i}. {title}")
        lines.append(f"- 저자: {authors}")
        lines.append(f"- 게재: {journal} ({pub_date})")
        lines.append(f"- 링크: {link}")
        lines.append("")
    return "\n".join(lines)

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    items = search_papers(KEYWORD, NUM_PAPERS)
    markdown = build_markdown(items, KEYWORD)

    today = date.today().isoformat()
    dated_path = os.path.join(RESULTS_DIR, f"{today}.md")
    latest_path = os.path.join(RESULTS_DIR, "latest.md")

    with open(dated_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"완료: {dated_path} 및 {latest_path} 생성됨")

if __name__ == "__main__":
    main()