"""
FRC Scouting 周期统计数据结构定义
定义了 calculate_cycle_statistics 函数的标准返回值格式
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, asdict, field
import json
import os


# why use Set?
# because we need the set operation | & - +


@dataclass
class MatchStatistics:
    """完整比赛的周期统计数据"""

    file_name: str = ""
    timestamp: int = 0
    tournament_level: str = ""
    match_no: int = 0
    team_no: int = 0
    event_code: str = ""

    score_coral: "ScoreCoralStatistics" = field(
        default_factory=lambda: ScoreCoralStatistics()
    )
    intake_coral: "IntakeCoralStatistics" = field(
        default_factory=lambda: IntakeCoralStatistics()
    )
    score_algae: "ScoreAlgaeStatistics" = field(
        default_factory=lambda: ScoreAlgaeStatistics()
    )
    intake_algae: "IntakeAlgaeStatistics" = field(
        default_factory=lambda: IntakeAlgaeStatistics()
    )
    defense: "DefenseStatistics" = field(default_factory=lambda: DefenseStatistics())
    foul: "FoulStatistics" = field(default_factory=lambda: FoulStatistics())
    give_up: "GiveUpStatistics" = field(default_factory=lambda: GiveUpStatistics())
    climb_up: "ClimbUpStatistics" = field(default_factory=lambda: ClimbUpStatistics())
    leave: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，处理Set类型的序列化"""
        result = asdict(self)

        # 递归处理所有Set类型，转换为list
        def convert_sets_to_lists(obj):
            if isinstance(obj, dict):
                return {k: convert_sets_to_lists(v) for k, v in obj.items()}
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, list):
                return [convert_sets_to_lists(item) for item in obj]
            else:
                return obj

        return convert_sets_to_lists(result)

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save_to_json_file(self, filepath: str) -> None:
        """保存到JSON文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_json_file(cls, filepath: str) -> "MatchStatistics":
        """从JSON文件恢复数据"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        match_statistics = cls._from_dict(data)
        match_statistics.timestamp = (
            os.path.splitext(os.path.basename(filepath))[0]
        ).split("_")[-1]
        match_statistics.file_name = os.path.basename(filepath)
        return match_statistics

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "MatchStatistics":
        """从字典恢复数据，处理Set类型的反序列化"""

        # 处理 ScoreCoralStatistics
        score_coral_data = data.get("score_coral", {})
        score_coral = ScoreCoralStatistics(
            cycle_times=score_coral_data.get("cycle_times", []),
            faces=score_coral_data.get("faces", []),
            auto_index=set(score_coral_data.get("auto_index", [])),
            stack_l1_index=set(score_coral_data.get("stack_l1_index", [])),
            l1_index=set(score_coral_data.get("l1_index", [])),
            l2_index=set(score_coral_data.get("l2_index", [])),
            l3_index=set(score_coral_data.get("l3_index", [])),
            l4_index=set(score_coral_data.get("l4_index", [])),
            successful_index=set(score_coral_data.get("successful_index", [])),
            defended_index=set(score_coral_data.get("defended_index", [])),
        )

        # 处理 IntakeCoralStatistics
        intake_coral_data = data.get("intake_coral", {})
        intake_coral = IntakeCoralStatistics(
            auto_load_station_cnt=intake_coral_data.get("auto_load_station_cnt", 0),
            auto_ground_cnt=intake_coral_data.get("auto_ground_cnt", 0),
            auto_fixed_cnt=intake_coral_data.get("auto_fixed_cnt", 0),
            teleop_load_station_cnt=intake_coral_data.get("teleop_load_station_cnt", 0),
            teleop_ground_cnt=intake_coral_data.get("teleop_ground_cnt", 0),
            teleop_fixed_cnt=intake_coral_data.get("teleop_fixed_cnt", 0),
        )

        # 处理 ScoreAlgaeStatistics
        score_algae_data = data.get("score_algae", {})
        score_algae = ScoreAlgaeStatistics(
            cycle_times=score_algae_data.get("cycle_times", []),
            auto_index=set(score_algae_data.get("auto_index", [])),
            place_net_index=set(score_algae_data.get("place_net_index", [])),
            shoot_net_index=set(score_algae_data.get("shoot_net_index", [])),
            processor_index=set(score_algae_data.get("processor_index", [])),
            last_sec_processor_index=set(
                score_algae_data.get("last_sec_processor_index", [])
            ),
            tactical_index=set(score_algae_data.get("tactical_index", [])),
            success_index=set(score_algae_data.get("success_index", [])),
            defended_index=set(score_algae_data.get("defended_index", [])),
        )

        # 处理 IntakeAlgaeStatistics
        intake_algae_data = data.get("intake_algae", {})
        intake_algae = IntakeAlgaeStatistics(
            auto_ground_front_cnt=intake_algae_data.get("auto_ground_front_cnt", 0),
            auto_ground_middle_cnt=intake_algae_data.get("auto_ground_middle_cnt", 0),
            auto_ground_back_cnt=intake_algae_data.get("auto_ground_back_cnt", 0),
            auto_reef_cnt=intake_algae_data.get("auto_reef_cnt", 0),
            auto_scrape_cnt=intake_algae_data.get("auto_scrape_cnt", 0),
            teleop_ground_front_cnt=intake_algae_data.get("teleop_ground_front_cnt", 0),
            teleop_ground_middle_cnt=intake_algae_data.get(
                "teleop_ground_middle_cnt", 0
            ),
            teleop_ground_back_cnt=intake_algae_data.get("teleop_ground_back_cnt", 0),
            teleop_reef_cnt=intake_algae_data.get("teleop_reef_cnt", 0),
            teleop_scrape_cnt=intake_algae_data.get("teleop_scrape_cnt", 0),
        )

        # 处理 DefenseStatistics
        defense_data = data.get("defense", {})
        defense = DefenseStatistics(cycle_times=defense_data.get("cycle_times", []))

        # 处理 FoulStatistics
        foul_data = data.get("foul", {})
        foul = FoulStatistics(cnt=foul_data.get("cnt", 0))

        # 处理 GiveUpStatistics
        give_up_data = data.get("give_up", {})
        give_up = GiveUpStatistics(cycle_times=give_up_data.get("cycle_times", []))

        # 处理 ClimbUpStatistics
        climb_up_data = data.get("climb_up", {})
        climb_up = ClimbUpStatistics(
            time=climb_up_data.get("time", 0.0),
            duration=climb_up_data.get("duration", 0.0),
            status=climb_up_data.get("status", ""),
        )
        leave = data.get("leave", False)
        return cls(
            score_coral=score_coral,
            intake_coral=intake_coral,
            score_algae=score_algae,
            intake_algae=intake_algae,
            defense=defense,
            foul=foul,
            give_up=give_up,
            climb_up=climb_up,
            tournament_level=data.get("tournament_level", ""),
            match_no=data.get("match_no", 0),
            team_no=data.get("team_no", 0),
            event_code=data.get("event_code", ""),
            leave=leave,
        )

    def get_coral_teleop_time(self) -> float:
        """获取手动阶段珊瑚任务总时间"""
        return self.score_coral.get_teleop_total_time()

    def get_algae_teleop_time(self) -> float:
        """获取手动阶段藻类任务总时间"""
        return self.score_algae.get_teleop_total_time()

    def get_defense_total_time(self) -> float:
        """获取防守任务总时间"""
        return self.defense.get_total_time()

    def get_give_up_total_time(self) -> float:
        """获取放弃任务总时间"""
        return self.give_up.get_total_time()

    def get_teleop_task_times(self) -> Dict[str, float]:
        """获取手动阶段各类任务的时间"""
        return {
            "coral": self.get_coral_teleop_time(),
            "algae": self.get_algae_teleop_time(),
            "defense": self.get_defense_total_time(),
            "give_up": self.get_give_up_total_time(),
        }

    def get_teleop_task_time_ratios(self) -> Dict[str, float]:
        """获取手动阶段各类任务的时间占比（相对于135秒）"""
        times = self.get_teleop_task_times()
        return {task: time / 135.0 for task, time in times.items()}


@dataclass
class ScoreCoralStatistics:
    cycle_times: List[float] = field(default_factory=list)
    faces: List[int] = field(default_factory=list)
    auto_index: Set[int] = field(default_factory=set)
    stack_l1_index: Set[int] = field(default_factory=set)
    l1_index: Set[int] = field(default_factory=set)
    l2_index: Set[int] = field(default_factory=set)
    l3_index: Set[int] = field(default_factory=set)
    l4_index: Set[int] = field(default_factory=set)
    successful_index: Set[int] = field(default_factory=set)
    defended_index: Set[int] = field(default_factory=set)

    def get_avg_cycle_time(self) -> float:
        return (
            sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 999.0
        )

    def get_avg_successful_undefended_cycle_time(self) -> float:
        successful_undefended_index = (
            self.successful_index - self.defended_index
        ) - self.auto_index
        successful_undefended_cycle_time = [
            self.cycle_times[index] for index in successful_undefended_index
        ]
        return (
            sum(successful_undefended_cycle_time)
            / len(successful_undefended_cycle_time)
            if successful_undefended_cycle_time
            else 999.0
        )

    def get_teleop_total_time(self) -> float:
        """获取手动阶段总时间"""
        teleop_index = set(range(len(self.cycle_times))) - self.auto_index
        teleop_cycle_times = [self.cycle_times[index] for index in teleop_index]
        return sum(teleop_cycle_times)


@dataclass
class IntakeCoralStatistics:
    auto_load_station_cnt: int = 0
    auto_ground_cnt: int = 0
    auto_fixed_cnt: int = 0
    teleop_load_station_cnt: int = 0
    teleop_ground_cnt: int = 0
    teleop_fixed_cnt: int = 0


@dataclass
class ScoreAlgaeStatistics:
    cycle_times: List[float] = field(default_factory=list)
    auto_index: Set[int] = field(default_factory=set)
    place_net_index: Set[int] = field(default_factory=set)
    shoot_net_index: Set[int] = field(default_factory=set)
    processor_index: Set[int] = field(default_factory=set)
    last_sec_processor_index: Set[int] = field(default_factory=set)
    tactical_index: Set[int] = field(default_factory=set)
    success_index: Set[int] = field(default_factory=set)
    defended_index: Set[int] = field(default_factory=set)

    def get_avg_cycle_time(self) -> float:
        """获取平均周期时间"""
        return (
            sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 999.0
        )

    def get_avg_successful_undefended_cycle_time(self) -> float:
        successful_undefended_index = (
            self.success_index - self.defended_index
        ) - self.auto_index
        successful_undefended_cycle_time = [
            self.cycle_times[index] for index in successful_undefended_index
        ]
        return (
            sum(successful_undefended_cycle_time)
            / len(successful_undefended_cycle_time)
            if successful_undefended_cycle_time
            else 999.0
        )

    def get_teleop_total_time(self) -> float:
        """获取手动阶段总时间"""
        teleop_index = set(range(len(self.cycle_times))) - self.auto_index
        teleop_cycle_times = [self.cycle_times[index] for index in teleop_index]
        return sum(teleop_cycle_times)


@dataclass
class IntakeAlgaeStatistics:
    auto_ground_front_cnt: int = 0
    auto_ground_middle_cnt: int = 0
    auto_ground_back_cnt: int = 0
    auto_reef_cnt: int = 0
    auto_scrape_cnt: int = 0
    teleop_ground_front_cnt: int = 0
    teleop_ground_middle_cnt: int = 0
    teleop_ground_back_cnt: int = 0
    teleop_reef_cnt: int = 0
    teleop_scrape_cnt: int = 0


@dataclass
class DefenseStatistics:
    cycle_times: List[float] = field(default_factory=list)

    def get_avg_cycle_time(self) -> float:
        """获取平均周期时间"""
        return (
            sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 0.0
        )

    def get_total_time(self) -> float:
        """获取总时间"""
        return sum(self.cycle_times)


@dataclass
class FoulStatistics:
    cnt: int = 0


@dataclass
class GiveUpStatistics:
    cycle_times: List[float] = field(default_factory=list)

    def get_avg_cycle_time(self) -> float:
        """获取平均周期时间"""
        return (
            sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 0.0
        )

    def get_total_time(self) -> float:
        """获取总时间"""
        return sum(self.cycle_times)


@dataclass
class ClimbUpStatistics:
    time: float = 0.0
    duration: float = 0.0
    status: str = ""


if __name__ == "__main__":
    match_statistics = MatchStatistics.from_json_file(
        "backend/match_records/processed/match_record_SY_2910_Playoff_2_1751982952463.json"
    )
    print(match_statistics.timestamp)
