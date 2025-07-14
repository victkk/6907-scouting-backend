import re
import os
import shutil
import logging

logger = logging.getLogger(__name__)

TRASH_RAW_DIR = os.path.join(os.path.dirname(__file__), "match_records", "trash", "raw")
TRASH_PROCESSED_DIR = os.path.join(
    os.path.dirname(__file__), "match_records", "trash", "processed"
)
os.makedirs(TRASH_RAW_DIR, exist_ok=True)
os.makedirs(TRASH_PROCESSED_DIR, exist_ok=True)
# 配置文件路径
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "match_records", "raw")
PROCESSED_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "match_records", "processed"
)
TEAM_SHORTCUTS_FILE = os.path.join(os.path.dirname(__file__), "team_shortcuts.json")
ATTRIBUTE_SHORTCUTS_FILE = os.path.join(
    os.path.dirname(__file__), "attribute_shortcuts.json"
)

# 确保目录存在
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


def parse_filename(filename):
    """解析文件名，提取tournament_level, match_no, timestamp等信息"""
    # 文件名格式: match_record_{eventCode}_{teamNo}_{tournamentLevel}_{matchNo}_{timestamp}.json
    match = re.match(r"match_record_(.+)_(\d+)_(.+)_(\d+)_(\d+)\.json", filename)
    if match:
        event_code = match.group(1)
        team_no = int(match.group(2))
        tournament_level = match.group(3)
        match_no = int(match.group(4))
        timestamp = int(match.group(5))
        return {
            "event_code": event_code,
            "team_no": team_no,
            "tournament_level": tournament_level,
            "match_no": match_no,
            "timestamp": timestamp,
            "filename": filename,
        }
    return None


def get_file_list(include_trash=False):
    """获取文件列表，支持排序"""
    files = []

    # 获取正常文件
    raw_files = set([f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")])
    processed_files = set(
        [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith(".json")]
    )
    active_files = raw_files.intersection(processed_files)

    for filename in active_files:
        file_info = parse_filename(filename)
        if file_info:
            file_info["status"] = "active"
            files.append(file_info)

    # 获取回收站文件
    if include_trash:
        trash_raw_files = set(
            [f for f in os.listdir(TRASH_RAW_DIR) if f.endswith(".json")]
        )
        trash_processed_files = set(
            [f for f in os.listdir(TRASH_PROCESSED_DIR) if f.endswith(".json")]
        )
        trash_files = trash_raw_files.intersection(trash_processed_files)

        for filename in trash_files:
            file_info = parse_filename(filename)
            if file_info:
                file_info["status"] = "trash"
                files.append(file_info)

    # 按tournament_level, match_no, timestamp排序
    def sort_key(file_info):
        # 为tournament_level分配权重，Practice < Qualification < Playoff
        level_weight = {"Practice": 1, "Qualification": 2, "Playoff": 3}
        return (
            level_weight.get(file_info["tournament_level"], 0),
            file_info["match_no"],
            file_info["timestamp"],
        )

    files.sort(key=sort_key)
    return files


def move_files_to_trash(filenames):
    """将文件移动到回收站"""
    success_count = 0
    errors = []

    for filename in filenames:
        try:
            # 移动raw文件
            raw_src = os.path.join(RAW_DATA_DIR, filename)
            raw_dst = os.path.join(TRASH_RAW_DIR, filename)
            if os.path.exists(raw_src):
                shutil.move(raw_src, raw_dst)

            # 移动processed文件
            processed_src = os.path.join(PROCESSED_DATA_DIR, filename)
            processed_dst = os.path.join(TRASH_PROCESSED_DIR, filename)
            if os.path.exists(processed_src):
                shutil.move(processed_src, processed_dst)

            success_count += 1
            logger.info(f"已将文件移动到回收站: {filename}")

        except Exception as e:
            errors.append(f"移动文件 {filename} 失败: {str(e)}")
            logger.error(f"移动文件到回收站失败: {filename}, 错误: {str(e)}")

    return success_count, errors


def restore_files_from_trash(filenames):
    """从回收站恢复文件"""
    success_count = 0
    errors = []

    for filename in filenames:
        try:
            # 恢复raw文件
            raw_src = os.path.join(TRASH_RAW_DIR, filename)
            raw_dst = os.path.join(RAW_DATA_DIR, filename)
            if os.path.exists(raw_src):
                shutil.move(raw_src, raw_dst)

            # 恢复processed文件
            processed_src = os.path.join(TRASH_PROCESSED_DIR, filename)
            processed_dst = os.path.join(PROCESSED_DATA_DIR, filename)
            if os.path.exists(processed_src):
                shutil.move(processed_src, processed_dst)

            success_count += 1
            logger.info(f"已从回收站恢复文件: {filename}")

        except Exception as e:
            errors.append(f"恢复文件 {filename} 失败: {str(e)}")
            logger.error(f"从回收站恢复文件失败: {filename}, 错误: {str(e)}")

    return success_count, errors


def permanently_delete_files(filenames):
    """永久删除文件"""
    success_count = 0
    errors = []

    for filename in filenames:
        try:
            # 删除raw文件
            raw_path = os.path.join(TRASH_RAW_DIR, filename)
            if os.path.exists(raw_path):
                os.remove(raw_path)

            # 删除processed文件
            processed_path = os.path.join(TRASH_PROCESSED_DIR, filename)
            if os.path.exists(processed_path):
                os.remove(processed_path)

            success_count += 1
            logger.info(f"已永久删除文件: {filename}")

        except Exception as e:
            errors.append(f"永久删除文件 {filename} 失败: {str(e)}")
            logger.error(f"永久删除文件失败: {filename}, 错误: {str(e)}")

    return success_count, errors
