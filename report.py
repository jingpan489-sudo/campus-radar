"""简报生成模块（Markdown）"""
import os
from datetime import datetime, date
from typing import List
from scrapers.base import JobItem
import config


REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def _match_keywords(job: JobItem) -> bool:
    """判断岗位是否命中产品运营关键词"""
    text = f"{job.title} {job.category} {job.tags}"
    # 优先按类别命中
    for cat_kw in config.CATEGORY_KEYWORDS:
        if cat_kw in job.category:
            return True
    # 再按标题关键词兜底
    all_kw = []
    for kws in config.KEYWORDS.values():
        all_kw.extend(kws)
    return any(kw in text for kw in all_kw)


def _match_city(job: JobItem) -> bool:
    """判断岗位是否在目标城市（空配置=不限）"""
    if not config.TARGET_CITIES:
        return True
    loc = job.location or ""
    # 全国/多地岗位也保留
    if not loc or "全国" in loc:
        return True
    return any(city in loc for city in config.TARGET_CITIES)


def filter_jobs(jobs: List[JobItem]) -> List[JobItem]:
    """按关键词+城市过滤岗位"""
    return [j for j in jobs if _match_keywords(j) and _match_city(j)]


def generate_brief(jobs: List[JobItem], new_keys: set, all_raw_count: dict) -> str:
    """生成当日 Markdown 简报"""
    today = date.today().isoformat()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 过滤出目标岗位
    target_jobs = filter_jobs(jobs)
    # 标记新增
    for j in target_jobs:
        j._is_new = j.dedup_key in new_keys

    new_jobs = [j for j in target_jobs if getattr(j, "_is_new", False)]
    existing_jobs = [j for j in target_jobs if not getattr(j, "_is_new", False)]

    lines = []
    lines.append(f"# 📋 秋招雷达日报 · {today}")
    lines.append("")
    lines.append(f"> 自动抓取于 {now} ｜ 关注方向：产品 / 运营 ｜ 目标城市：{('、'.join(config.TARGET_CITIES)) or '全国'}")
    lines.append("")

    # 总览
    lines.append("## 📊 今日总览")
    lines.append("")
    lines.append("| 公司 | 抓取岗位总数 | 命中产品/运营 | 今日新增 |")
    lines.append("|------|------------|-------------|---------|")
    for company, cnt in all_raw_count.items():
        hit = len([j for j in target_jobs if j.company == company])
        new = len([j for j in new_jobs if j.company == company])
        lines.append(f"| {company} | {cnt} | {hit} | {new if new else '-'} |")
    lines.append("")

    # 新增岗位
    if new_jobs:
        lines.append("## 🆕 今日新增岗位")
        lines.append("")
        by_company = {}
        for j in new_jobs:
            by_company.setdefault(j.company, []).append(j)
        for company in sorted(by_company.keys()):
            lines.append(f"### {company}")
            lines.append("")
            lines.append("| 岗位名称 | 类别 | 地点 | 发布时间 | 标签 | 链接 |")
            lines.append("|---------|------|------|---------|------|------|")
            for j in by_company[company]:
                link = f"[查看]({j.url})" if j.url else "-"
                lines.append(
                    f"| {j.title} | {j.category or '-'} | {j.location or '-'} | "
                    f"{j.publish_time or '-'} | {j.tags or '-'} | {link} |"
                )
            lines.append("")
    else:
        lines.append("## 🆕 今日新增岗位")
        lines.append("")
        lines.append("今日暂无新增的目标岗位。各公司官网一旦放出新的产品/运营岗，次日简报会自动列出。")
        lines.append("")

    # 在招岗位存量（命中的，便于随时查阅）
    if existing_jobs:
        lines.append("## 📌 当前在招（产品/运营方向）")
        lines.append("")
        lines.append("<details><summary>点击展开全部在招岗位</summary>")
        lines.append("")
        by_company = {}
        for j in existing_jobs:
            by_company.setdefault(j.company, []).append(j)
        for company in sorted(by_company.keys()):
            lines.append(f"**{company}**")
            lines.append("")
            for j in by_company[company]:
                link = f"[查看]({j.url})" if j.url else ""
                tag_str = f"`{j.tags}`" if j.tags else ""
                lines.append(f"- {j.title} ｜ {j.category or ''} ｜ {j.location or ''} ｜ {j.publish_time or ''} {tag_str} {link}")
            lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("---")
    lines.append("*本简报由 Campus Radar 自动生成。如某公司持续显示 0 岗位，可能是其校招尚未开启，开启后会自动出现。*")

    content = "\n".join(lines)

    # 写文件
    os.makedirs(REPORT_DIR, exist_ok=True)
    filepath = os.path.join(REPORT_DIR, f"{today}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return content
