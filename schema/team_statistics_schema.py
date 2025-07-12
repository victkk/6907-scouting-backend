"""
FRC 2025 Scouting 单个队伍统计数据结构定义
包含完整的队伍统计项目

注：
- 筒指coral，球指algae，狗洞指processor，网指net
- 除自动、BPS、EPA数据板块外，别的数据只用手动的数据来算
- 带有（场次号）的都指单场的最值（top3），要显示最值发生的场次号，如并列则显示最晚的场次号
- 带有（升序）/（降序）的要显示队伍单项数据所在赛区排名
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import json
import os


@dataclass
class RankValue:
    """带排名的数据"""

    value: float = 0.0
    rank: int = -1


@dataclass
class RankValueMatch(RankValue):
    """带场次号的数值数据"""

    match_no: int = 0
    tournament_level: str = ""


@dataclass
class MatchList:
    """各场次号数据"""

    match_nos: List[int] = field(default_factory=list)
    tournament_levels: List[str] = field(default_factory=list)


@dataclass
class TeamStatistics:
    """单个队伍完整统计数据"""

    # 1. 基本车况
    team_no: int = 0

    # 2. cycle数据 - 时间占比
    cycle_teleop_coral_time_ratio: RankValue = field(default_factory=RankValue)
    cycle_teleop_algae_time_ratio: RankValue = field(default_factory=RankValue)
    cycle_teleop_defense_time_ratio: RankValue = field(default_factory=RankValue)
    cycle_teleop_give_up_time_ratio: RankValue = field(default_factory=RankValue)

    # 3. 爬升&狗洞
    climb_success_matches: MatchList = field(default_factory=MatchList)
    climb_fail_matches: MatchList = field(default_factory=MatchList)
    climb_touch_chain_matches: MatchList = field(default_factory=MatchList)
    climb_success_percentage: RankValue = field(default_factory=RankValue)
    climb_success_cycle_time_min: RankValueMatch = field(default_factory=RankValueMatch)
    climb_park_time_median: RankValue = field(default_factory=RankValue)

    processor_success_max_single_match: RankValueMatch = field(
        default_factory=RankValueMatch
    )

    # 4. BPS (Branches per second)
    bps_value: RankValue = field(default_factory=RankValue)

    # 5. EPA (Extra points added per second)
    epa_value: RankValue = field(default_factory=RankValue)

    # points per match
    ppg_avg: RankValue = field(default_factory=RankValue)
    ppg_max_single_match: RankValueMatch = field(default_factory=RankValueMatch)

    # 6. 自动阶段
    auto_line_cross_percentage: RankValue = field(default_factory=RankValue)
    auto_preload_coral_percentage: RankValue = field(default_factory=RankValue)
    auto_high_mid_coral_max: RankValueMatch = field(default_factory=RankValueMatch)
    auto_high_mid_coral_success_rate: RankValue = field(default_factory=RankValue)
    auto_low_slot_coral_max: RankValueMatch = field(default_factory=RankValueMatch)
    auto_low_slot_coral_success_rate: RankValue = field(default_factory=RankValue)
    auto_net_place_max: RankValueMatch = field(default_factory=RankValueMatch)
    auto_algae_process_max: RankValueMatch = field(default_factory=RankValueMatch)

    # 7. 手动筒
    # 筒来源统计
    coral_source_station_percentage: RankValue = field(default_factory=RankValue)
    coral_source_ground_percentage: RankValue = field(default_factory=RankValue)

    l1_teleop_success_count_avg: RankValue = field(default_factory=RankValue)
    l1_teleop_success_percentage: RankValue = field(default_factory=RankValue)
    l2_teleop_success_count_avg: RankValue = field(default_factory=RankValue)
    l2_teleop_success_percentage: RankValue = field(default_factory=RankValue)
    l3_teleop_success_count_avg: RankValue = field(default_factory=RankValue)
    l3_teleop_success_percentage: RankValue = field(default_factory=RankValue)
    l4_teleop_success_count_avg: RankValue = field(default_factory=RankValue)
    l4_teleop_success_percentage: RankValue = field(default_factory=RankValue)
    stack_l1_teleop_success_count_avg: RankValue = field(default_factory=RankValue)
    stack_l1_teleop_success_percentage: RankValue = field(default_factory=RankValue)

    l1_teleop_undefended_success_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    l2_teleop_undefended_success_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    l3_teleop_undefended_success_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    l4_teleop_undefended_success_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    stack_l1_teleop_undefended_success_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )

    total_teleop_success_count_avg: RankValue = field(default_factory=RankValue)
    total_teleop_success_percentage: RankValue = field(default_factory=RankValue)
    total_teleop_undefended_success_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )

    # 8. 手动球

    avg_scrape_algae_count: RankValue = field(default_factory=RankValue)
    avg_pickup_algae_count: RankValue = field(default_factory=RankValue)
    algae_success_cycle_count_median: RankValue = field(default_factory=RankValue)
    algae_success_cycle_count_max: RankValueMatch = field(
        default_factory=RankValueMatch
    )
    net_success_undefended_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    algae_source_reef_percentage: RankValue = field(default_factory=RankValue)
    algae_source_back_percentage: RankValue = field(default_factory=RankValue)
    algae_source_mid_percentage: RankValue = field(default_factory=RankValue)
    algae_source_front_percentage: RankValue = field(default_factory=RankValue)

    # 网投统计
    net_place_percentage: RankValue = field(default_factory=RankValue)
    net_shoot_percentage: RankValue = field(default_factory=RankValue)
    net_place_success_rate: RankValue = field(default_factory=RankValue)
    net_shoot_success_rate: RankValue = field(default_factory=RankValue)
    tactical_max_single_match: RankValueMatch = field(default_factory=RankValueMatch)
    last_second_processer_matches: MatchList = field(default_factory=MatchList)

    # 9. 防守抗性
    coral_defended_percentage: RankValue = field(default_factory=RankValue)
    coral_defended_max_single_match: RankValueMatch = field(
        default_factory=RankValueMatch
    )
    defended_success_coral_cycle_time_max: RankValueMatch = field(
        default_factory=RankValueMatch
    )
    defended_success_coral_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    undefended_success_coral_cycle_time_median: RankValue = field(
        default_factory=RankValue
    )
    defended_vs_undefended_success_coral_cycle_time_increase_percentage: RankValue = (
        field(default_factory=RankValue)
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {}

        def convert_field(obj):
            if isinstance(obj, (RankValue, RankValueMatch)):
                return obj.__dict__
            elif isinstance(obj, MatchList):
                return obj.__dict__
            elif isinstance(obj, dict):
                return {k: convert_field(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_field(item) for item in obj]
            else:
                return obj

        for field_name, field_value in self.__dict__.items():
            result[field_name] = convert_field(field_value)

        return result

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save_to_json_file(self, filepath: str) -> None:
        """保存到JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_json_file(cls, filepath: str) -> "TeamStatistics":
        """从JSON文件恢复数据"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "TeamStatistics":
        """从字典恢复数据"""

        def restore_field(field_data, field_type):
            if field_type == RankValue:
                return RankValue(
                    value=field_data.get("value", 0.0), rank=field_data.get("rank", -1)
                )
            elif field_type == RankValueMatch:
                return RankValueMatch(
                    value=field_data.get("value", 0.0),
                    rank=field_data.get("rank", -1),
                    match_no=field_data.get("match_no", 0),
                    tournament_level=field_data.get("tournament_level", ""),
                )
            elif field_type == MatchList:
                return MatchList(
                    match_nos=field_data.get("match_nos", []),
                    tournament_levels=field_data.get("tournament_levels", []),
                )
            else:
                return field_data

        # 创建实例
        instance = cls()

        # 恢复基本字段
        instance.team_no = data.get("team_no", 0)

        # 恢复基础时间数据
        instance.cycle_teleop_coral_time_ratio = restore_field(
            data.get("cycle_teleop_coral_time_ratio", {}), RankValue
        )
        instance.cycle_teleop_algae_time_ratio = restore_field(
            data.get("cycle_teleop_algae_time_ratio", {}), RankValue
        )
        instance.cycle_teleop_defense_time_ratio = restore_field(
            data.get("cycle_teleop_defense_time_ratio", {}), RankValue
        )
        instance.cycle_teleop_give_up_time_ratio = restore_field(
            data.get("cycle_teleop_give_up_time_ratio", {}), RankValue
        )

        # 恢复爬升相关
        instance.climb_success_matches = restore_field(
            data.get("climb_success_matches", {}), MatchList
        )
        instance.climb_fail_matches = restore_field(
            data.get("climb_fail_matches", {}), MatchList
        )
        instance.climb_touch_chain_matches = restore_field(
            data.get("climb_touch_chain_matches", {}), MatchList
        )
        instance.climb_success_percentage = restore_field(
            data.get("climb_success_percentage", {}), RankValue
        )
        instance.climb_success_cycle_time_min = restore_field(
            data.get("climb_success_cycle_time_min", {}), RankValueMatch
        )
        instance.climb_approach_time_median = restore_field(
            data.get("climb_approach_time_median", {}), RankValue
        )
        instance.processor_success_max_single_match = restore_field(
            data.get("processor_success_max_single_match", {}), RankValueMatch
        )

        # 恢复BPS和EPA
        instance.bps_value = restore_field(data.get("bps_value", {}), RankValue)
        instance.epa_value = restore_field(data.get("epa_value", {}), RankValue)

        # 恢复自动阶段数据
        instance.auto_line_cross_percentage = restore_field(
            data.get("auto_line_cross_percentage", {}), RankValue
        )
        instance.auto_preload_coral_percentage = restore_field(
            data.get("auto_preload_coral_percentage", {}), RankValue
        )
        instance.auto_high_mid_coral_max = restore_field(
            data.get("auto_high_mid_coral_max", {}), RankValueMatch
        )
        instance.auto_high_mid_coral_success_rate = restore_field(
            data.get("auto_high_mid_coral_success_rate", {}), RankValue
        )
        instance.auto_low_slot_coral_max = restore_field(
            data.get("auto_low_slot_coral_max", {}), RankValueMatch
        )
        instance.auto_low_slot_coral_success_rate = restore_field(
            data.get("auto_low_slot_coral_success_rate", {}), RankValue
        )
        instance.auto_net_place_max = restore_field(
            data.get("auto_net_place_max", {}), RankValueMatch
        )
        instance.auto_algae_process_max = restore_field(
            data.get("auto_algae_process_max", {}), RankValueMatch
        )

        # 恢复手动筒基础数据
        instance.coral_source_station_percentage = restore_field(
            data.get("coral_source_station_percentage", {}), RankValue
        )
        instance.coral_source_ground_percentage = restore_field(
            data.get("coral_source_ground_percentage", {}), RankValue
        )
        instance.coral_success_cycle_median = restore_field(
            data.get("coral_success_cycle_median", {}), RankValue
        )
        instance.coral_success_cycle_max = restore_field(
            data.get("coral_success_cycle_max", {}), RankValueMatch
        )
        instance.coral_undefended_cycle_time_median = restore_field(
            data.get("coral_undefended_cycle_time_median", {}), RankValue
        )

        # 恢复各级别筒统计
        instance.high_coral_avg_success = restore_field(
            data.get("high_coral_avg_success", {}), RankValue
        )
        instance.high_coral_success_rate = restore_field(
            data.get("high_coral_success_rate", {}), RankValue
        )
        instance.high_coral_undefended_success_cycle_time_median = restore_field(
            data.get("high_coral_undefended_success_cycle_time_median", {}), RankValue
        )

        instance.mid_coral_avg_success = restore_field(
            data.get("mid_coral_avg_success", {}), RankValue
        )
        instance.mid_coral_success_rate = restore_field(
            data.get("mid_coral_success_rate", {}), RankValue
        )
        instance.mid_coral_undefended_success_cycle_time_median = restore_field(
            data.get("mid_coral_undefended_success_cycle_time_median", {}), RankValue
        )

        instance.low_coral_avg_success = restore_field(
            data.get("low_coral_avg_success", {}), RankValue
        )
        instance.low_coral_success_rate = restore_field(
            data.get("low_coral_success_rate", {}), RankValue
        )
        instance.low_coral_undefended_success_cycle_time_median = restore_field(
            data.get("low_coral_undefended_success_cycle_time_median", {}), RankValue
        )

        instance.slot_coral_avg_success = restore_field(
            data.get("slot_coral_avg_success", {}), RankValue
        )
        instance.slot_coral_success_rate = restore_field(
            data.get("slot_coral_success_rate", {}), RankValue
        )
        instance.slot_coral_undefended_success_cycle_time_median = restore_field(
            data.get("slot_coral_undefended_success_cycle_time_median", {}), RankValue
        )

        # 恢复网+洞+背面槽筒统计
        instance.net_processor_back_slot_avg_success = restore_field(
            data.get("net_processor_back_slot_avg_success", {}), RankValue
        )
        instance.net_processor_back_slot_success_rate = restore_field(
            data.get("net_processor_back_slot_success_rate", {}), RankValue
        )
        instance.net_processor_back_slot_undefended_success_cycle_time_median = (
            restore_field(
                data.get(
                    "net_processor_back_slot_undefended_success_cycle_time_median", {}
                ),
                RankValue,
            )
        )
        instance.net_processor_back_coral_undefended_count = restore_field(
            data.get("net_processor_back_coral_undefended_count", {}), RankValue
        )

        # 恢复叠筒统计
        instance.stack_coral_max_single_match = restore_field(
            data.get("stack_coral_max_single_match", {}), RankValue
        )
        instance.stack_coral_success_rate = restore_field(
            data.get("stack_coral_success_rate", {}), RankValue
        )
        instance.stack_coral_undefended_success_cycle_time_median = restore_field(
            data.get("stack_coral_undefended_success_cycle_time_median", {}), RankValue
        )

        # 恢复手动球数据
        instance.algae_success_cycle_median = restore_field(
            data.get("algae_success_cycle_median", {}), RankValue
        )
        instance.algae_success_cycle_max = restore_field(
            data.get("algae_success_cycle_max", {}), RankValueMatch
        )
        instance.avg_scrape_algae_count = restore_field(
            data.get("avg_scrape_algae_count", {}), RankValue
        )
        instance.avg_pickup_algae_count = restore_field(
            data.get("avg_pickup_algae_count", {}), RankValue
        )

        # 恢复球来源统计
        instance.algae_source_coral_percentage = data.get(
            "algae_source_coral_percentage", 0.0
        )
        instance.algae_source_back_percentage = data.get(
            "algae_source_back_percentage", 0.0
        )
        instance.algae_source_mid_percentage = data.get(
            "algae_source_mid_percentage", 0.0
        )
        instance.algae_source_front_percentage = data.get(
            "algae_source_front_percentage", 0.0
        )

        # 恢复网投统计
        instance.net_place_percentage = data.get("net_place_percentage", 0.0)
        instance.net_shoot_percentage = data.get("net_shoot_percentage", 0.0)
        instance.net_place_success_rate = restore_field(
            data.get("net_place_success_rate", {}), RankValue
        )
        instance.net_shoot_success_rate = restore_field(
            data.get("net_shoot_success_rate", {}), RankValue
        )

        # 恢复战术相关
        instance.tactical_max_single_match = restore_field(
            data.get("tactical_max_single_match", {}), RankValueMatch
        )
        instance.last_second_processer_matches = restore_field(
            data.get("last_second_processer_matches", {}), MatchList
        )

        # 恢复防守抗性
        instance.coral_defended_percentage = restore_field(
            data.get("coral_defended_percentage", {}), RankValue
        )
        instance.coral_defended_max_single_match = restore_field(
            data.get("coral_defended_max_single_match", {}), RankValueMatch
        )
        instance.defended_success_coral_cycle_time_max = restore_field(
            data.get("defended_success_coral_cycle_time_max", {}), RankValueMatch
        )
        instance.defended_success_coral_cycle_time_median = restore_field(
            data.get("defended_success_coral_cycle_time_median", {}), RankValue
        )
        instance.undefended_success_coral_cycle_time_median = restore_field(
            data.get("undefended_success_coral_cycle_time_median", {}), RankValue
        )
        instance.defended_vs_undefended_success_coral_cycle_time_increase_percentage = restore_field(
            data.get(
                "defended_vs_undefended_success_coral_cycle_time_increase_percentage",
                {},
            ),
            RankValue,
        )

        return instance


# 辅助函数用于创建和管理统计数据
def create_team_statistics(team_no: int) -> TeamStatistics:
    """创建一个新的队伍统计实例"""
    return TeamStatistics(team_no=team_no)


def calculate_rank_data(
    teams_data: List[TeamStatistics], field_name: str, descending: bool = True
) -> None:
    """计算指定字段的排名并更新到队伍数据中"""
    # 获取所有队伍的指定字段值
    team_values = []
    for team in teams_data:
        field_obj = getattr(team, field_name)
        if isinstance(field_obj, (RankValue, RankValueMatch)):
            team_values.append((team, field_obj.value))
        else:
            # 如果是普通数值类型
            team_values.append((team, field_obj))

    # 排序
    team_values.sort(key=lambda x: x[1], reverse=descending)

    # 分配排名
    for rank, (team, value) in enumerate(team_values, 1):
        field_obj = getattr(team, field_name)
        if isinstance(field_obj, (RankValue, RankValueMatch)):
            field_obj.rank = rank
