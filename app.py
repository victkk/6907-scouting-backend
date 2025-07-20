from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from werkzeug.exceptions import BadRequest
import uuid
import shutil
import re
from backend.service.analyze_single_file import calculate_single_match_record_statistics
from backend.schema.match_statistics_schema import MatchStatistics
from backend.service.aggregate_team_statistics import (
    create_team_statistics_from_matches,
)
from backend.schema.team_statistics_schema import TeamStatistics
from dataclasses import fields
from backend.utils import *

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def perform_initial_statistics():
    """
    执行初始统计
    """
    raw_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    processed_files = [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith(".json")]
    for raw_file in raw_files:
        if raw_file not in processed_files:
            with open(os.path.join(RAW_DATA_DIR, raw_file), "r", encoding="utf-8") as f:
                data = json.load(f)
                match_statistics: MatchStatistics = (
                    calculate_single_match_record_statistics(data)
                )
                processed_filepath = os.path.join(PROCESSED_DATA_DIR, raw_file)
                match_statistics.save_to_json_file(processed_filepath)
                logger.info(f"成功保存比赛记录: {raw_file}")
    logger.info("初始统计完成")


@app.route("/api/match-records", methods=["POST"])
def upload_match_record():
    """
    接收前端传输的比赛记录JSON数据
    """
    try:
        # 检查请求是否包含JSON数据
        if not request.is_json:
            return jsonify({"success": False, "message": "请求必须包含JSON数据"}), 400

        # 获取JSON数据
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "无效的JSON数据"}), 400

        # 验证必要字段
        required_fields = ["teamNo", "matchNumber", "eventCode"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f'缺少必要字段: {", ".join(missing_fields)}',
                    }
                ),
                400,
            )

        # 生成文件名
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        team_no = data.get("teamNo")
        match_no = data.get("matchNumber")
        event_code = data.get("eventCode")
        tournament_level = data.get("tournamentLevel")
        filename = f"match_record_{event_code}_{team_no}_{tournament_level}_{match_no}_{timestamp}.json"
        filepath = os.path.join(RAW_DATA_DIR, filename)

        # 添加服务器接收时间戳
        data["serverReceivedTimestamp"] = datetime.datetime.now().isoformat()
        data["filename"] = filename

        # 保存到文件
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        match_statistics: MatchStatistics = calculate_single_match_record_statistics(
            data
        )
        processed_filepath = os.path.join(PROCESSED_DATA_DIR, filename)
        match_statistics.save_to_json_file(processed_filepath)
        logger.info(f"成功保存比赛记录: {filename}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "比赛记录上传成功",
                    "filename": filename,
                    "timestamp": data["serverReceivedTimestamp"],
                }
            ),
            201,
        )

    except BadRequest:
        return jsonify({"success": False, "message": "请求格式错误"}), 400
    except Exception as e:
        logger.error(f"上传比赛记录失败: {str(e)}")
        return jsonify({"success": False, "message": f"服务器内部错误: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """
    健康检查接口
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "version": "1.0.0",
            }
        ),
        200,
    )


@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "接口不存在"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "message": "服务器内部错误"}), 500


# 新增：获取所有处理过的比赛数据
def get_all_match_statistics():
    """获取所有已处理的比赛统计数据"""
    processed_files = [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith(".json")]
    match_stats = []

    for filename in processed_files:
        filepath = os.path.join(PROCESSED_DATA_DIR, filename)
        try:
            match_stat = MatchStatistics.from_json_file(filepath)
            match_stats.append(match_stat)
        except Exception as e:
            logger.error(f"读取文件 {filename} 时出错: {str(e)}")

    return match_stats


# 新增：获取队伍快捷方式配置
def get_team_shortcuts():
    """获取队伍快捷方式配置"""
    try:
        with open(TEAM_SHORTCUTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("队伍快捷方式配置文件不存在")
        return {}
    except Exception as e:
        logger.error(f"读取队伍快捷方式配置时出错: {str(e)}")
        return {}


# 新增：获取属性快捷方式配置
def get_attribute_shortcuts():
    """获取属性快捷方式配置"""
    try:
        with open(ATTRIBUTE_SHORTCUTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("属性快捷方式配置文件不存在")
        return {}
    except Exception as e:
        logger.error(f"读取属性快捷方式配置时出错: {str(e)}")
        return {}


# 新增：保存快捷方式配置
def save_shortcut(name, shortcut_type, items):
    """保存快捷方式配置"""
    try:
        if shortcut_type == "team":
            # 队伍快捷组
            shortcuts = get_team_shortcuts()
            shortcuts[name] = items
            with open(TEAM_SHORTCUTS_FILE, "w", encoding="utf-8") as f:
                json.dump(shortcuts, f, ensure_ascii=False, indent=2)
        else:
            # 属性快捷组
            shortcuts = get_attribute_shortcuts()
            shortcuts[name] = items
            with open(ATTRIBUTE_SHORTCUTS_FILE, "w", encoding="utf-8") as f:
                json.dump(shortcuts, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        logger.error(f"保存快捷方式配置时出错: {str(e)}")
        return False


# 新增：删除快捷方式配置
def delete_shortcut(name, shortcut_type):
    """删除快捷方式配置"""
    try:
        if shortcut_type == "team":
            # 队伍快捷组
            shortcuts = get_team_shortcuts()
            if name in shortcuts:
                del shortcuts[name]
                with open(TEAM_SHORTCUTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(shortcuts, f, ensure_ascii=False, indent=2)
                return True
            else:
                return False
        else:
            # 属性快捷组
            shortcuts = get_attribute_shortcuts()
            if name in shortcuts:
                del shortcuts[name]
                with open(ATTRIBUTE_SHORTCUTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(shortcuts, f, ensure_ascii=False, indent=2)
                return True
            else:
                return False
    except Exception as e:
        logger.error(f"删除快捷方式配置时出错: {str(e)}")
        return False


# 新增：Web页面路由
@app.route("/")
def index():
    """主页 - 队伍能力比较页面"""
    return render_template("comparison.html")


@app.route("/ranking")
def ranking():
    """排名展示页面"""
    return render_template("ranking.html")


# 新增：API端点 - 获取队伍统计数据
@app.route("/api/team-statistics", methods=["GET"])
def get_team_statistics():
    """获取队伍统计数据"""
    try:
        # 获取查询参数
        teams = request.args.getlist("teams")  # 选择的队伍
        tournament_levels = request.args.getlist("tournament_levels")  # 选择的比赛等级
        match_nos = request.args.getlist("match_nos")  # 选择的比赛场次

        # 获取所有比赛数据
        match_stats = get_all_match_statistics()

        # 过滤比赛数据
        def filter_matches(match_stat):
            # 过滤掉不需要的比赛等级
            if (
                tournament_levels
                and match_stat.tournament_level not in tournament_levels
            ):
                return True
            # 过滤掉不需要的比赛场次
            if match_nos and str(match_stat.match_no) not in match_nos:
                return True
            return False

        # 创建队伍统计数据
        team_statistics = create_team_statistics_from_matches(
            match_stats, filter_matches
        )
        # 过滤掉不需要的队伍
        if teams:
            team_statistics = [
                team_stat
                for team_stat in team_statistics
                if str(team_stat.team_no) in teams
            ]
        # 转换为字典格式
        result = []
        for team_stat in team_statistics:
            result.append(team_stat.to_dict())

        return jsonify({"success": True, "data": result, "total_teams": len(result)})

    except Exception as e:
        logger.error(f"获取队伍统计数据时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 获取队伍快捷方式
@app.route("/api/team-shortcuts", methods=["GET"])
def get_team_shortcuts_api():
    """获取队伍快捷方式配置"""
    try:
        shortcuts = get_team_shortcuts()
        return jsonify({"success": True, "data": shortcuts})
    except Exception as e:
        logger.error(f"获取队伍快捷方式时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 获取属性快捷方式
@app.route("/api/attribute-shortcuts", methods=["GET"])
def get_attribute_shortcuts_api():
    """获取属性快捷方式配置"""
    try:
        shortcuts = get_attribute_shortcuts()
        return jsonify({"success": True, "data": shortcuts})
    except Exception as e:
        logger.error(f"获取属性快捷方式时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 保存快捷方式
@app.route("/api/shortcuts", methods=["POST"])
def save_shortcuts_api():
    """保存快捷方式配置"""
    try:
        if not request.is_json:
            return jsonify({"success": False, "message": "请求必须是JSON格式"}), 400

        data = request.get_json()

        # 验证必要字段
        required_fields = ["name", "type", "items"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"success": False, "message": f"缺少必要字段: {field}"}),
                    400,
                )

        name = data["name"]
        shortcut_type = data["type"]
        items = data["items"]

        # 验证类型
        if shortcut_type not in ["team", "attribute"]:
            return (
                jsonify(
                    {"success": False, "message": "快捷组类型必须是 team 或 attribute"}
                ),
                400,
            )

        # 验证项目
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({"success": False, "message": "项目列表不能为空"}), 400

        # 保存快捷方式
        if save_shortcut(name, shortcut_type, items):
            return jsonify({"success": True, "message": "快捷组创建成功"})
        else:
            return jsonify({"success": False, "message": "保存快捷组失败"}), 500

    except Exception as e:
        logger.error(f"保存快捷方式时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 删除快捷方式
@app.route("/api/shortcuts/<name>/<shortcut_type>", methods=["DELETE"])
def delete_shortcut_api(name, shortcut_type):
    """删除快捷方式配置"""
    try:
        if delete_shortcut(name, shortcut_type):
            return jsonify({"success": True, "message": "快捷组删除成功"})
        else:
            return jsonify({"success": False, "message": "快捷组不存在"}), 404
    except Exception as e:
        logger.error(f"删除快捷方式时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 修改快捷方式
@app.route("/api/shortcuts/<old_name>/<shortcut_type>", methods=["PUT"])
def update_shortcut_api(old_name, shortcut_type):
    """修改快捷方式配置"""
    try:
        if not request.is_json:
            return jsonify({"success": False, "message": "请求必须是JSON格式"}), 400

        data = request.get_json()

        # 验证必要字段
        required_fields = ["name", "items"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"success": False, "message": f"缺少必要字段: {field}"}),
                    400,
                )

        new_name = data["name"]
        items = data["items"]

        # 验证项目
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({"success": False, "message": "项目列表不能为空"}), 400

        # 获取现有快捷组
        if shortcut_type == "team":
            shortcuts = get_team_shortcuts()
        else:
            shortcuts = get_attribute_shortcuts()

        # 检查原名称是否存在
        if old_name not in shortcuts:
            return jsonify({"success": False, "message": "要修改的快捷组不存在"}), 404

        # 如果名称改变了，检查新名称是否已存在
        if old_name != new_name and new_name in shortcuts:
            return jsonify({"success": False, "message": "新的快捷组名称已存在"}), 400

        # 删除原快捷组（如果名称改变了）
        if old_name != new_name:
            del shortcuts[old_name]

        # 保存新的快捷组
        if save_shortcut(new_name, shortcut_type, items):
            return jsonify({"success": True, "message": "快捷组修改成功"})
        else:
            return jsonify({"success": False, "message": "保存快捷组失败"}), 500

    except Exception as e:
        logger.error(f"修改快捷方式时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 获取所有可用队伍
@app.route("/api/teams", methods=["GET"])
def get_all_teams():
    """获取所有可用队伍"""
    try:
        match_stats = get_all_match_statistics()
        teams = list(set(match_stat.team_no for match_stat in match_stats))
        teams.sort()

        return jsonify({"success": True, "data": teams})
    except Exception as e:
        logger.error(f"获取队伍列表时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 获取所有可用比赛等级
@app.route("/api/tournament-levels", methods=["GET"])
def get_tournament_levels():
    """获取所有可用比赛等级"""
    try:
        match_stats = get_all_match_statistics()
        levels = list(set(match_stat.tournament_level for match_stat in match_stats))
        levels.sort()

        return jsonify({"success": True, "data": levels})
    except Exception as e:
        logger.error(f"获取比赛等级列表时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route("/api/all-team-attributes", methods=["GET"])
def get_all_team_attributes():
    """获取所有可用队伍属性"""
    try:

        attributes = [field.name for field in fields(TeamStatistics)]
        attributes.sort()
        return jsonify({"success": True, "data": attributes})
    except Exception as e:
        logger.error(f"获取队伍属性列表时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 新增：API端点 - 获取排名数据
@app.route("/api/rankings", methods=["GET"])
def get_rankings():
    """获取排名数据"""
    try:
        # 获取查询参数
        attributes = request.args.getlist("attributes")  # 排名属性列表
        tournament_levels = request.args.getlist("tournament_levels")  # 选择的比赛等级
        match_nos = request.args.getlist("match_nos")  # 选择的比赛场次

        # 获取所有比赛数据
        match_stats = get_all_match_statistics()

        # 过滤比赛数据
        def filter_matches(match_stat):
            if (
                tournament_levels
                and match_stat.tournament_level not in tournament_levels
            ):
                return True
            # 过滤掉不需要的比赛场次
            if match_nos and str(match_stat.match_no) not in match_nos:
                return True
            return False

        # 创建队伍统计数据
        team_statistics = create_team_statistics_from_matches(
            match_stats, filter_matches
        )

        # 提取所有请求属性的排名数据
        all_ranking_data = {}

        for attribute in attributes:
            ranking_data = []
            for team_stat in team_statistics:
                team_dict = team_stat.to_dict()
                if attribute in team_dict:
                    attr_data = team_dict[attribute]
                    if (
                        isinstance(attr_data, dict)
                        and "value" in attr_data
                        and "rank" in attr_data
                    ):
                        ranking_data.append(
                            {
                                "team_no": team_stat.team_no,
                                "value": attr_data["value"],
                                "rank": attr_data["rank"],
                                "match_no": attr_data.get("match_no"),
                                "tournament_level": attr_data.get("tournament_level"),
                            }
                        )

            # 按排名排序
            ranking_data.sort(
                key=lambda x: x["rank"] if x["rank"] > 0 else float("inf")
            )
            all_ranking_data[attribute] = ranking_data

        return jsonify(
            {"success": True, "data": all_ranking_data, "attributes": attributes}
        )

    except Exception as e:
        logger.error(f"获取排名数据时出错: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route("/file-manager")
def file_manager():
    """文件管理页面"""
    return render_template("file_manager.html")


@app.route("/api/files", methods=["GET"])
def get_files():
    """获取文件列表API"""
    try:
        include_trash = request.args.get("include_trash", "false").lower() == "true"
        files = get_file_list(include_trash)
        return jsonify({"success": True, "files": files, "total": len(files)})
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        return (
            jsonify({"success": False, "message": f"获取文件列表失败: {str(e)}"}),
            500,
        )


@app.route("/api/files/move-to-trash", methods=["POST"])
def move_to_trash():
    """移动文件到回收站API"""
    try:
        data = request.get_json()
        filenames = data.get("filenames", [])

        if not filenames:
            return jsonify({"success": False, "message": "请选择要移动的文件"}), 400

        success_count, errors = move_files_to_trash(filenames)

        return jsonify(
            {
                "success": True,
                "message": f"成功移动 {success_count} 个文件到回收站",
                "success_count": success_count,
                "errors": errors,
            }
        )

    except Exception as e:
        logger.error(f"移动文件到回收站失败: {str(e)}")
        return (
            jsonify({"success": False, "message": f"移动文件到回收站失败: {str(e)}"}),
            500,
        )


@app.route("/api/files/restore", methods=["POST"])
def restore_from_trash():
    """从回收站恢复文件API"""
    try:
        data = request.get_json()
        filenames = data.get("filenames", [])

        if not filenames:
            return jsonify({"success": False, "message": "请选择要恢复的文件"}), 400

        success_count, errors = restore_files_from_trash(filenames)

        return jsonify(
            {
                "success": True,
                "message": f"成功恢复 {success_count} 个文件",
                "success_count": success_count,
                "errors": errors,
            }
        )

    except Exception as e:
        logger.error(f"从回收站恢复文件失败: {str(e)}")
        return (
            jsonify({"success": False, "message": f"从回收站恢复文件失败: {str(e)}"}),
            500,
        )


@app.route("/api/files/delete", methods=["POST"])
def permanently_delete():
    """永久删除文件API"""
    try:
        data = request.get_json()
        filenames = data.get("filenames", [])

        if not filenames:
            return jsonify({"success": False, "message": "请选择要删除的文件"}), 400

        success_count, errors = permanently_delete_files(filenames)

        return jsonify(
            {
                "success": True,
                "message": f"成功永久删除 {success_count} 个文件",
                "success_count": success_count,
                "errors": errors,
            }
        )

    except Exception as e:
        logger.error(f"永久删除文件失败: {str(e)}")
        return (
            jsonify({"success": False, "message": f"永久删除文件失败: {str(e)}"}),
            500,
        )


if __name__ == "__main__":
    logger.info("启动FRC Scouting后端服务...")
    logger.info(f"原始数据目录: {RAW_DATA_DIR}")
    logger.info(f"处理后数据目录: {PROCESSED_DATA_DIR}")
    perform_initial_statistics()
    # 启动Flask应用
    app.run(host="0.0.0.0", port=5000, debug=True)
    # 开放给公网
