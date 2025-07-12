#!/usr/bin/env python
"""
FRC Scout 数据显示网站启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 现在导入并运行应用
from backend.app import app, logger, perform_initial_statistics

if __name__ == "__main__":
    logger.info("启动FRC Scouting数据显示网站...")
    logger.info("=" * 50)
    logger.info("项目信息:")
    logger.info(f"- 项目根目录: {project_root}")
    logger.info(f"- 后端目录: {current_dir}")
    logger.info("=" * 50)

    # 执行初始统计
    perform_initial_statistics()

    logger.info("=" * 50)
    logger.info("访问地址:")
    logger.info("- 主页(队伍比较): http://localhost:5000")
    logger.info("- 排名展示: http://localhost:5000/ranking")
    logger.info("- API健康检查: http://localhost:5000/api/health")
    logger.info("=" * 50)

    # 启动Flask应用
    app.run(host="0.0.0.0", port=5000, debug=True)
