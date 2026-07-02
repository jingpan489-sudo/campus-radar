"""
Campus Radar —— 秋招岗位雷达
每日抓取各官网校招岗位，对比识别新增，生成 Markdown 简报。

用法:
    python main.py            # 跑一次，生成当日简报
    python main.py --full     # 全量抓取但不标记新增（首次初始化用）
"""
import sys
import os
import traceback
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config
from scrapers import SCRAPERS
from scrapers.base import JobItem
import store
import report
import push


def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": config.USER_AGENT})
    retry = Retry(total=config.MAX_RETRIES, backoff_factor=1,
                  status_forcelist=[500, 502, 503, 504],
                  allowed_methods=["GET", "POST"])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def main():
    full_mode = "--full" in sys.argv
    session = make_session()
    all_jobs = []
    raw_counts = {}

    print("=" * 50)
    print(f"Campus Radar 启动 ｜ 模式: {'全量初始化' if full_mode else '日常抓取'}")
    print("=" * 50)

    for name, cls in SCRAPERS.items():
        if not config.ENABLED_COMPANIES.get(name, True):
            print(f"[{name}] 已跳过（配置关闭）")
            continue
        print(f"\n[{name}] 抓取中...")
        try:
            scraper = cls(session)
            jobs = scraper.fetch()
            all_jobs.extend(jobs)
            raw_counts[name] = len(jobs)
            print(f"  ✅ 获取 {len(jobs)} 个岗位")
        except Exception as e:
            print(f"  ❌ 抓取失败: {e}")
            traceback.print_exc()
            raw_counts[name] = 0

    # 加载通用抓取源（零代码添加的新公司）
    from scrapers.generic import GenericScraper
    for src_cfg in getattr(config, "GENERIC_SOURCES", []):
        name = src_cfg.get("name", "未知")
        print(f"\n[{name}] 抓取中...(通用抓取器)")
        try:
            scraper = GenericScraper(session, src_cfg)
            jobs = scraper.fetch()
            all_jobs.extend(jobs)
            raw_counts[name] = len(jobs)
            print(f"  ✅ 获取 {len(jobs)} 个岗位")
        except Exception as e:
            print(f"  ❌ 抓取失败: {e}")
            traceback.print_exc()
            raw_counts[name] = 0

    # 保存到数据库
    if full_mode:
        # 全量初始化模式：先清空再写入，不标记新增
        store.clear_all()
        store.save_jobs(all_jobs)
        new_keys = set()  # 初始化不报新增
    else:
        new_keys = store.save_jobs(all_jobs)

    total_new = len(new_keys)
    print(f"\n{'=' * 50}")
    print(f"抓取完成：共 {len(all_jobs)} 个岗位，本次新增 {total_new} 个")
    print(f"数据库累计：{store.get_all_jobs_count()} 个岗位")

    # 生成简报
    content = report.generate_brief(all_jobs, new_keys, raw_counts)
    today = date.today().isoformat()
    report_path = os.path.join("reports", f"{today}.md")
    print(f"\n📄 简报已生成：{report_path}")
    print("=" * 50)

    # 推送简报到微信等渠道（需配置环境变量）
    print("\n📤 推送简报...")
    today_str = date.today().isoformat()
    push.send_brief(content, title=f"秋招雷达日报 {today_str}")
    return content


if __name__ == "__main__":
    main()
