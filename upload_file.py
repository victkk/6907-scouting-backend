#!/usr/bin/env python3
"""
单文件上传脚本 - 将本地JSON文件上传到FRC Scout接口
"""

import requests
import json
import sys
import os
import argparse
from typing import Dict, Any, Optional


def validate_json_data(data: Dict[str, Any]) -> bool:
    """验证JSON数据是否包含必需字段"""
    required_fields = ["teamNo", "matchNumber", "eventCode"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        print(f"❌ 缺少必需字段: {', '.join(missing_fields)}")
        return False

    return True


def read_and_validate_file(file_path: str) -> Optional[Dict[str, Any]]:
    """读取并验证JSON文件"""
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None

        # 检查文件扩展名
        if not file_path.lower().endswith(".json"):
            print(f"❌ 文件必须是JSON格式: {file_path}")
            return None

        # 读取文件
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 验证数据
        if not validate_json_data(data):
            return None

        print(f"✅ 文件验证通过: {file_path}")
        return data

    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None


def upload_file(file_path: str, host: str = "localhost", port: int = 5000) -> bool:
    """上传文件到接口"""
    # 读取并验证文件
    data = read_and_validate_file(file_path)
    if not data:
        return False

    # 构建URL
    url = f"https://{host}/api/match-records"

    try:
        print(f"📤 正在上传到: {url}")

        # 发送请求
        response = requests.post(
            url, json=data, headers={"Content-Type": "application/json"}, timeout=30
        )

        # 处理响应
        if response.status_code == 201:
            result = response.json()
            print("✅ 上传成功!")
            print(f"   文件名: {result.get('filename', 'N/A')}")
            print(f"   时间戳: {result.get('timestamp', 'N/A')}")
            print(f"   消息: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ 上传失败 (状态码: {response.status_code})")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data.get('message', '未知错误')}")
            except:
                print(f"   响应内容: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败: 无法连接到 {url}")
        print("   请确保服务器正在运行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 上传过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="将本地JSON文件上传到FRC Scout接口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python upload_file.py --file match_record.json
  python upload_file.py --file match_record.json --host 192.168.1.100 --port 8080
  python upload_file.py -f match_record.json -H localhost -p 5000
        """,
    )

    parser.add_argument("-f", "--file", required=True, help="要上传的JSON文件路径")

    parser.add_argument(
        "-H",
        "--host",
        default="6907goat.cc",
        help="服务器地址 (默认: localhost)",
    )

    parser.add_argument(
        "-p", "--port", type=int, default=5000, help="服务器端口 (默认: 5000)"
    )

    args = parser.parse_args()

    print("🚀 FRC Scout 文件上传工具")
    print("=" * 50)
    print(f"文件: {args.file}")
    print(f"服务器: {args.host}:{args.port}")
    print("=" * 50)

    # 执行上传
    success = upload_file(args.file, args.host, args.port)

    print("=" * 50)
    if success:
        print("🎉 上传完成!")
        sys.exit(0)
    else:
        print("💥 上传失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
