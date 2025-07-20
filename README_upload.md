# 文件上传脚本使用说明

## 概述

`upload_file.py` 是一个用于将本地 JSON 文件上传到 FRC Scout 接口的 Python 脚本。

## 安装依赖

确保已安装 `requests` 库：

```bash
pip install requests
```

## 使用方法

### 基本用法

```bash
python upload_file.py --file match_record.json
```

### 指定服务器地址和端口

```bash
python upload_file.py --file match_record.json --host 192.168.1.100 --port 8080
```

### 使用短参数

```bash
python upload_file.py -f match_record.json -H localhost -p 5000
```

## 参数说明

- `-f, --file`: 要上传的 JSON 文件路径（必需）
- `-H, --host`: 服务器地址（默认: localhost）
- `-p, --port`: 服务器端口（默认: 5000）

## 文件格式要求

上传的 JSON 文件必须包含以下必需字段：

- `teamNo`: 队伍编号
- `matchNumber`: 比赛编号
- `eventCode`: 赛事代码

## 示例

### 1. 上传单个文件

```bash
python upload_file.py --file backend/match_records/raw/match_record_SYOF_6706_Qualification_57_1752654955498.json
```

### 2. 上传到远程服务器

```bash
python upload_file.py --file match_record.json --host 192.168.1.100 --port 5000
```

## 输出示例

### 成功上传

```
🚀 FRC Scout 文件上传工具
==================================================
文件: match_record.json
服务器: localhost:5000
==================================================
✅ 文件验证通过: match_record.json
📤 正在上传到: http://localhost:5000/api/match-records
✅ 上传成功!
   文件名: match_record_SYOF_6706_Qualification_57_1752654955498.json
   时间戳: 2025-07-16T16:35:55.498979
   消息: 比赛记录上传成功
==================================================
🎉 上传完成!
```

### 上传失败

```
🚀 FRC Scout 文件上传工具
==================================================
文件: invalid_file.json
服务器: localhost:5000
==================================================
❌ 缺少必需字段: teamNo, matchNumber
==================================================
💥 上传失败!
```

## 错误处理

脚本会处理以下常见错误：

- 文件不存在
- JSON 格式错误
- 缺少必需字段
- 网络连接失败
- 服务器错误
- 请求超时

## 注意事项

1. 确保服务器正在运行
2. 确保 JSON 文件格式正确
3. 确保网络连接正常
4. 大文件可能需要更长的上传时间
