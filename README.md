# FRC Scout 数据分析网站

基于现有后端基础设施的 FRC 侦查数据展示网站，提供队伍比较和排名展示功能。

## 功能特性

### 1. 队伍比较页面

- **队伍选择**：通过复选框选择要比较的队伍
- **队伍搜索**：实时搜索队伍号，快速定位目标队伍
- **快捷组选择**：预设的队伍组合，快速选择常用队伍组合
- **数据过滤**：
  - 按比赛等级过滤（Practice、Qualification、Playoff 等）
  - 按比赛场次过滤（支持范围表达式，如"1-7,9-11,15"）
- **数据展示**：
  - 队伍作为列，统计属性作为行的矩阵表格
  - 支持多种数据类型显示（RankValue、RankValueMatch、float、MatchList）
  - 颜色编码的排名显示（金银铜牌样式）
- **数据导出**：CSV 格式导出比较结果

### 2. 排名展示页面

- **多属性排名**：可同时选择多个属性进行排名对比
- **属性搜索**：实时搜索属性名称，快速查找目标属性
- **属性快捷组**：预设的属性组合，快速选择常用属性组合
- **数据过滤**：
  - 按比赛等级过滤
  - 按比赛场次过滤（支持范围表达式）
- **排名展示**：
  - 双行表头格式，清晰展示属性名称
  - 排名、数值和队伍号分列显示
  - 排名颜色编码（前三名突出显示）
- **数据导出**：CSV 格式导出排名结果

### 3. 快捷组管理

- **创建快捷组**：支持创建队伍快捷组和属性快捷组
- **编辑快捷组**：修改现有快捷组的名称和包含的项目
- **删除快捷组**：删除不需要的快捷组（含确认提示）
- **快捷组类型**：
  - 队伍快捷组：用于队伍比较页面
  - 属性快捷组：用于排名展示页面
- **动态管理**：网页端创建/修改/删除的快捷组会实时保存到服务器
- **快捷访问**：下拉选择旁的编辑和删除按钮，便于快速管理

### 4. 搜索功能

- **队伍搜索**：在比较页面搜索队伍号
- **属性搜索**：在排名页面搜索属性名称
- **实时过滤**：输入时实时更新显示结果

## 项目结构

```
backend/
├── app.py                      # Flask应用主文件
├── requirements.txt            # Python依赖
├── team_shortcuts.json         # 队伍快捷方式配置
├── attribute_shortcuts.json    # 属性快捷方式配置
├── templates/                  # HTML模板
│   ├── base.html              # 基础模板
│   ├── comparison.html        # 队伍比较页面
│   └── ranking.html           # 排名展示页面
├── static/                    # 静态资源
│   ├── css/
│   │   └── style.css          # 样式文件
│   └── js/
│       ├── common.js          # 通用JavaScript函数
│       ├── comparison.js      # 队伍比较页面脚本
│       └── ranking.js         # 排名展示页面脚本
├── match_records/             # 比赛记录数据
│   ├── raw/                   # 原始数据
│   └── processed/             # 处理后数据
├── schema/                    # 数据模式
│   ├── match_statistics_schema.py
│   └── team_statistics_schema.py
└── service/                   # 服务层
    ├── analyze_single_file.py
    └── aggregate_team_statistics.py
```

## API 接口

### 队伍数据相关

- `GET /api/teams` - 获取所有可用队伍
- `GET /api/team-statistics` - 获取队伍统计数据
- `GET /api/team-shortcuts` - 获取队伍快捷方式配置

### 排名数据相关

- `GET /api/rankings` - 获取排名数据
- `GET /api/attribute-shortcuts` - 获取属性快捷方式配置

### 快捷组管理

- `POST /api/shortcuts` - 创建快捷组
- `PUT /api/shortcuts/<name>/<type>` - 修改快捷组
- `DELETE /api/shortcuts/<name>/<type>` - 删除快捷组

### 系统相关

- `GET /api/tournament-levels` - 获取所有可用比赛等级
- `GET /api/health` - 健康检查

## 数据类型说明

### RankValue

包含数值和排名信息：

```json
{
  "value": 1.23,
  "rank": 5
}
```

### RankValueMatch

包含数值、排名和最佳表现比赛信息：

```json
{
  "value": 45.6,
  "rank": 2,
  "match_no": 15,
  "tournament_level": "Qualification"
}
```

### MatchList

比赛组合列表：

```json
["Practice_1", "Practice_2", "Qualification_3"]
```

## 快捷组配置

### 队伍快捷组 (team_shortcuts.json)

```json
{
  "强队组合": [2910, 6907, 1751, 2333, 5678],
  "新队组合": [1001, 1002, 1003, 1004, 1005],
  "联盟一": [2910, 6907, 1751],
  "联盟二": [2333, 5678, 9999],
  "全部队伍": [2910, 6907, 1751, 2333, 5678, 1001, 1002, 1003, 1004, 1005, 9999]
}
```

### 属性快捷组 (attribute_shortcuts.json)

```json
{
  "核心指标": ["bps_value", "epa_value"],
  "自动阶段": [
    "auto_line_cross_percentage",
    "auto_preload_coral_percentage",
    "auto_high_mid_coral_success_rate"
  ],
  "爬升相关": [
    "climb_success_percentage",
    "climb_success_cycle_time_min",
    "climb_park_time_median"
  ],
  "筒任务": [
    "l1_teleop_success_percentage",
    "l2_teleop_success_percentage",
    "l3_teleop_success_percentage",
    "l4_teleop_success_percentage"
  ],
  "球任务": [
    "avg_scrape_algae_count",
    "avg_pickup_algae_count",
    "net_place_success_rate",
    "net_shoot_success_rate"
  ],
  "时间分配": [
    "cycle_teleop_coral_time_ratio",
    "cycle_teleop_algae_time_ratio",
    "cycle_teleop_defense_time_ratio"
  ]
}
```

## 安装和运行

### 依赖安装

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

### 访问地址

- 主页（队伍比较）：http://localhost:5000
- 排名展示：http://localhost:5000/ranking

## 使用说明

### 队伍比较

1. 选择要比较的队伍（可使用快捷组或手动选择）
2. 设置数据过滤条件（比赛等级、场次）
3. 点击"刷新数据"获取比较结果
4. 查看表格中的队伍统计对比
5. 点击"导出数据"保存结果

### 排名展示

1. 选择要排名的属性（可使用快捷组或手动选择）
2. 设置数据过滤条件
3. 点击"刷新排名"获取排名结果
4. 查看双列格式的排名表格（排名、数值、队伍）
5. 点击"导出排名"保存结果

### 比赛场次过滤

支持灵活的场次过滤表达式：

- 单个场次：`5`
- 范围：`1-7`
- 多个场次：`1,3,5`
- 复合表达式：`1-7,9-11,15`

### 快捷组管理

1. 点击"创建快捷组"按钮
2. 选择快捷组类型（队伍或属性）
3. 输入快捷组名称
4. 选择要包含的项目
5. 点击"保存快捷组"

#### 编辑快捷组

1. 从下拉列表中选择要编辑的快捷组
2. 点击编辑按钮（黄色铅笔图标）
3. 修改快捷组名称或选择的项目
4. 点击"保存修改"

#### 删除快捷组

1. 从下拉列表中选择要删除的快捷组
2. 点击删除按钮（红色垃圾桶图标）
3. 确认删除操作

## 技术栈

- **后端**：Flask (Python)
- **前端**：Bootstrap 5 + JavaScript
- **数据格式**：JSON
- **样式**：CSS3 + Font Awesome 图标

## 注意事项

1. 数据会自动从 processed 目录加载
2. 快捷组配置会实时保存到 JSON 文件
3. 排名颜色编码：金色（第 1 名）、银色（第 2 名）、铜色（第 3 名）
4. 所有数据导出为 UTF-8 编码的 CSV 文件
5. 页面支持响应式设计，适配不同屏幕尺寸
6. **快捷组管理**：
   - 删除快捷组操作不可撤销，请谨慎操作
   - 修改快捷组名称时，新名称不能与现有快捷组重名
   - 编辑和删除按钮只有在选择快捷组后才会启用
   - 快捷组类型在编辑时不可更改
