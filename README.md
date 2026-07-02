# 📡 Campus Radar · 秋招岗位雷达

每天自动抓取各大公司官网校招岗位，对比识别**新增岗位**，生成 Markdown 日报推送到微信。

专为 27 届秋招设计，关注**产品 / 运营**方向。

## ✨ 功能特性

- **6 大数据源**自动抓取：京东、快手、小红书、拼多多、淘宝（淘天）、OfferStar 聚合平台
- **新增检测**：对比历史数据，只报今天新出现的岗位，不打扰
- **智能过滤**：按产品/运营方向 + 目标城市过滤，只看关心的岗位
- **Markdown 日报**：按公司分组，含岗位名/类别/地点/发布时间/直达链接
- **GitHub Actions 定时**：每天自动运行，数据库随仓库持久化，零服务器
- **微信推送**：支持 Server酱 / 企业微信机器人，新岗位直达手机

## 📂 项目结构

```
campus-radar/
├── config.py              # ⭐ 配置文件（公司开关/关键词/城市）
├── main.py                # 主入口
├── push.py                # 微信推送模块
├── store.py               # 历史数据存储（SQLite）+ 新增对比
├── report.py              # 简报生成（Markdown）
├── scrapers/              # 各公司抓取器
│   ├── base.py            #   基类 + 统一数据结构
│   ├── jd.py              #   京东
│   ├── kuaishou.py        #   快手
│   ├── xiaohongshu.py     #   小红书
│   ├── pdd.py             #   拼多多
│   ├── taotian.py         #   淘宝(淘天)
│   └── offerstar.py       #   OfferStar 聚合平台
├── data/jobs.db           # 历史岗位数据库（自动生成）
├── reports/               # 每日简报（自动生成）
├── requirements.txt
└── .github/workflows/daily.yml  # GitHub Actions 定时任务
```

## 🚀 快速开始

### 本地运行

```bash
cd campus-radar
pip install -r requirements.txt

# 首次运行：全量初始化（不报新增，只建库）
python main.py --full

# 日常运行：对比历史，报告新增
python main.py
```

简报会生成在 `reports/YYYY-MM-DD.md`。

### GitHub Actions 自动运行（推荐）

1. **Fork 或推送本仓库到你的 GitHub**

2. **开启 Actions**：进入仓库 Settings → Actions → 确认允许运行

3. **（可选）配置微信推送**：
   - **Server酱**（推荐，免费推送到微信）：
     - 访问 [sct.ftqq.com](https://sct.ftqq.com/) 用微信扫码登录
     - 复制你的 `SendKey`
     - 仓库 Settings → Secrets and variables → Actions → New secret
     - Name 填 `PUSH_KEY`，Value 填你的 SendKey
   - **企业微信机器人**（备选）：
     - 企业微信群创建机器人，复制 Webhook 地址里的 key
     - 添加 Secret：Name 填 `WECOM_KEY`

4. **手动触发测试**：Actions 页面 → "秋招雷达日报" → Run workflow

之后每天北京时间 **09:00** 自动运行，简报会：
- 显示在 Actions 运行详情页的 Summary 里
- 自动 commit 到 `reports/` 目录归档
- 推送到你的微信（如已配置）

> **数据库持久化**：`data/jobs.db` 会随每次运行自动 commit 到仓库，保证下次运行能正确对比新增。

## ⚙️ 配置说明

编辑 `config.py` 即可定制：

### 增减监控公司

```python
ENABLED_COMPANIES = {
    "京东": True,
    "快手": True,
    # 把不想看的设为 False
}
```

### 修改岗位关键词

```python
KEYWORDS = {
    "产品": ["产品经理", "产品策划", "数据产品", ...],
    "运营": ["用户运营", "内容运营", "活动运营", ...],
    # 想加新方向直接加，比如：
    # "市场": ["市场策划", "品牌运营"],
}
```

### 修改目标城市

```python
TARGET_CITIES = ["上海", "北京", "杭州", "深圳", "广州"]
# 留空 [] 表示全国都看
```

## 📊 各公司当前抓取状态

截至工具开发时（2026年7月），各官网校招状态：

| 公司 | 接口 | 当前状态 | 产品/运营岗位 |
|------|------|---------|-------------|
| 京东 | 应届生招聘（含TET管培生） | ✅ 在招 | TET-产品方向 |
| 快手 | 27届快Star技术项目 | ✅ 在招 | 暂无（快Star为技术天才计划） |
| 小红书 | 校招应届生 | ✅ 在招（2026春招批次） | 3个产品技术岗 |
| 拼多多 | 27届校招（云弧计划） | ✅ 在招 | 1个产品岗 |
| 淘宝 | 26届秋招T-Star | ✅ 在招 | 暂无（T-Star为技术项目） |
| OfferStar | 聚合平台 | ✅ 持续更新 | 多家公司产品/运营公告 |

> 快手和淘宝当前只开了技术专项，产品/运营岗尚未开启——**这正是雷达的价值**：一旦开启，次日简报会自动列出。

## 🔧 技术说明

- 所有抓取均通过**官方 API 接口**或 SSR 页面获取，使用轻量 `requests` 库，无需浏览器
- 每个公司抓取器独立运行，互不影响（一个失败不影响其他）
- 数据库为 SQLite，单文件，随仓库版本管理
- 如某公司改版导致接口失效，对应抓取器会报错但其他公司继续运行

## ❓ 常见问题

**Q: 首次运行后简报显示"今日新增 0"？**
A: 首次用 `--full` 初始化，不报新增。之后日常运行才会对比新增。

**Q: 某公司一直显示 0 岗位？**
A: 该公司校招可能尚未开启（如快手/淘宝的产品运营岗），开启后会自动出现。也可能是接口改版，检查 Actions 运行日志。

**Q: GitHub Actions 没按时运行？**
A: GitHub cron 可能有 5-15 分钟延迟。如需精确时间，可在 workflow 里调整 cron 表达式。免费账户 cron 任务有数量限制。

**Q: 想加新公司？**
A: 在 `scrapers/` 下新建抓取器（继承 `BaseScraper`，实现 `fetch()`），在 `__init__.py` 和 `config.py` 里注册即可。
