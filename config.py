"""
Campus Radar 配置文件
修改这里的配置来定制你的秋招监控。
"""

# ==================== 监控公司开关 ====================
# 把不想监控的公司设为 False 即可
ENABLED_COMPANIES = {
    "京东": True,
    "快手": True,
    "小红书": True,
    "拼多多": True,
    "淘宝": True,
    "offerstar": True,   # 聚合平台，补充行业动态
}

# ==================== 岗位关键词 ====================
# 简报会优先按"职位类别"过滤，再用关键词对岗位标题做兜底匹配
# 想加方向直接往里加关键词即可
KEYWORDS = {
    "设计": [
        "景观", "景观设计", "方案设计", "施工图设计", "植物配置",
        "城市设计", "城市规划", "风景园林", "环境艺术",
        "室内设计", "建筑方案", "助理设计师", "设计实习生",
        "参数化设计", "BIM设计",
    ],
    "工程管理": [
        "项目管理", "工程管理", "项目监理", "工程监理",
        "成本控制", "工程造价", "招投标", "工程预算",
        "进度管理", "质量管理", "安全管理",
    ],
    "生态文旅": [
        "生态修复", "生态工程", "环境修复", "海绵城市",
        "乡村振兴", "文旅规划", "旅游规划", "景区规划",
        "湿地修复", "水生态", "碳中和", "双碳",
        "国土空间规划", "自然资源", "林业规划",
        "文旅项目", "度假区规划", "生态设计", "环境评估",
        "助理规划师", "生态实习生",
    ],
    "公共管理": [
        "公共管理", "行政管理", "政策研究", "城乡规划管理",
    ],
}

# 命中关键词的类别名（各公司 API 返回的类别字段里，含这些字就算命中）
CATEGORY_KEYWORDS = ["设计", "工程管理", "生态文旅", "公共管理", "景观"]

# ==================== 目标城市 ====================
# 留空 [] 表示全国都看；填了就只看这些城市
# 注意：部分公司（如小红书）按城市过滤，填这里会精确过滤
TARGET_CITIES = ["上海"]

# ==================== 各公司专属参数 ====================
COMPANY_CONFIG = {
    "京东": {
        # 应届生招聘类型，type=present 表示应届生
        "type": "present",
    },
    "快手": {
        # 27届校招项目代码（从官网 URL 里提取）
        "recruit_sub_project_codes": ["20271779425607"],
    },
    "小红书": {
        # term_regular = 应届生校招
        "campus_recruit_types": ["term_regular"],
        # workplace 城市编码（4401=上海）。留空则不限城市
        "workplaces": [],  # [] = 全国
    },
    "拼多多": {
        # t=null 表示全部类别，也可填具体类别 job code
        "t": None,
    },
    "淘宝": {
        # batchId 会自动获取，这里留默认即可
        "batch_channel": "campus_group_official_site",
    },
    "offerstar": {
        # 聚合平台查询参数
        "title": "2027",
        "positions": "运营",   # 聚合平台按"运营"方向筛
        "channel": "校招",
    },
}

# ==================== 通用抓取源（零代码添加新公司）====================
# 后续添加新公司，只需在这里加一段配置即可，无需写代码！
# 配置格式见 scrapers/generic.py 文件顶部说明。
#
# 示例（取消注释并修改即可启用）：
#
# GENERIC_SOURCES = [
#     {
#         "name": "某公司",
#         "type": "api",                          # api 或 html
#         "url": "https://example.com/api/jobs",
#         "method": "POST",
#         "headers": {"Content-Type": "application/json"},
#         "body_template": {"page": "{page}", "size": 100},
#         "pagination": {"page_start": 1, "page_key": "page", "stop_when": "less_than_size"},
#         "response": {"list_path": "data.list", "total_path": "data.total"},
#         "fields": {
#             "job_id": "id", "title": "positionName", "category": "jobType",
#             "location": "workCity", "publish_time": "createTime",
#         },
#         "detail_url_template": "https://example.com/jobs/{job_id}",
#         "timestamp_field": "createTime",
#     },
# ]
GENERIC_SOURCES = []

# ==================== 运行参数 ====================
# 请求超时（秒）
REQUEST_TIMEOUT = 20
# 失败重试次数
MAX_RETRIES = 2
# 每页抓取条数（尽量大，减少翻页）
PAGE_SIZE = 100
# User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
