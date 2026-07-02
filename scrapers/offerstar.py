"""OfferStar 聚合平台抓取器（SSR，直接解析 HTML 表格）
作为官网数据的补充，提供行业秋招动态
"""
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from .base import BaseScraper, JobItem
import config


class OfferstarScraper(BaseScraper):
    name = "offerstar"
    BASE = "https://www.offerstar.cn/recruitment"

    def fetch(self):
        cfg = config.COMPANY_CONFIG["offerstar"]
        title = cfg["title"]
        channel = cfg["channel"]
        # 对产品和运营两个方向各请求一次，合并去重
        seen_ids = set()
        all_items = []
        for position_kw in ["产品", "运营"]:
            url = f"{self.BASE}?title={quote(title)}&positions={quote(position_kw)}&channel={quote(channel)}"
            try:
                r = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                items = self._parse_html(r.text)
                for it in items:
                    if it.job_id not in seen_ids:
                        seen_ids.add(it.job_id)
                        all_items.append(it)
            except Exception as e:
                print(f"  [offerstar] 抓取 {position_kw} 方向失败: {e}")
        return all_items

    def _parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if not table:
            return []
        rows = table.find_all("tr")
        items = []
        for row in rows[1:]:  # 跳过表头
            cells = row.find_all(["td"])
            if len(cells) < 10:
                continue
            company = cells[0].get_text(strip=True)
            title = cells[1].get_text(strip=True)
            # cells[2]=批次, cells[3]=更新时间
            recruit_positions = cells[4].get_text(strip=True)   # 招聘岗位
            location = cells[5].get_text(strip=True)             # 工作地点
            # cells[6]=行业, cells[7]=招聘类型, cells[8]=截止时间
            # cells[9]=操作(投递链接)
            link = ""
            a = cells[9].find("a")
            if a and a.get("href"):
                link = a["href"]
            update_time = cells[3].get_text(strip=True)
            # 判断类别
            category = self._guess_category(recruit_positions + title)
            job_id = f"{company}_{title}"
            items.append(JobItem(
                company=f"offerstar·{company}",
                job_id=job_id,
                title=title,
                category=category,
                location=location,
                url=link,
                publish_time=update_time,
                tags="聚合",
            ))
        return items

    def _guess_category(self, text):
        cats = []
        for kw in config.CATEGORY_KEYWORDS:
            if kw in text:
                cats.append(kw)
        return "、".join(cats)
