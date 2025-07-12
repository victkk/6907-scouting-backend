"""
用于从原始的match_record.json提取出基础统计量
"""

from typing import List, Dict, Any, Optional
from backend.schema.match_statistics_schema import MatchStatistics


def calculate_single_match_record_statistics(
    match_record: Dict[str, Any],
) -> MatchStatistics:
    """
    计算单个文件的cycle时间统计数据

    Args:
        actions: 比赛动作列表

    Returns:
        MatchStatistics: 规范化的周期统计数据
    """
    actions = match_record.get("action")
    match_statistics = MatchStatistics(
        tournament_level=match_record.get("tournamentLevel"),
        match_no=match_record.get("matchNumber"),
        team_no=match_record.get("teamNo"),
        event_code=match_record.get("eventCode"),
    )
    process_cnt_statistics(match_statistics, actions)
    time_slices = _calculate_time_slices(actions)
    process_cycle_statistics(match_statistics, time_slices)
    return match_statistics


def process_cnt_statistics(
    match_statistics: MatchStatistics, actions: List[Dict[str, Any]]
):
    """
    处理计数统计
    """
    auto_actions, teleop_actions = split_actions_by_phase(actions)
    if len(auto_actions) > 1:
        match_statistics.leave = True
    else:
        match_statistics.leave = False

    for action in auto_actions:
        if action.get("type") == "intake coral":
            if action.get("intake coral type") in ["load station A", "load station B"]:
                match_statistics.intake_coral.auto_load_station_cnt += 1
            elif action.get("intake coral type") == "ground":
                match_statistics.intake_coral.auto_ground_cnt += 1
            elif action.get("intake coral type") == "fixed":
                match_statistics.intake_coral.auto_fixed_cnt += 1
            else:
                raise ValueError(
                    f"Unknown intake coral type: {action.get('intake coral type')}"
                )
        elif action.get("type") == "intake algae":
            if action.get("intake algae type") == "ground":
                if action.get("ground algae source") == "front":
                    match_statistics.intake_algae.auto_ground_front_cnt += 1
                elif action.get("ground algae source") == "middle":
                    match_statistics.intake_algae.auto_ground_middle_cnt += 1
                elif action.get("ground algae source") == "back":
                    match_statistics.intake_algae.auto_ground_back_cnt += 1
                else:
                    raise ValueError(
                        f"Unknown ground algae source: {action.get('ground algae source')}"
                    )
            elif action.get("intake algae type") == "reef":
                match_statistics.intake_algae.auto_reef_cnt += 1
            elif action.get("intake algae type") == "scrape":
                match_statistics.intake_algae.auto_scrape_cnt += 1
            else:
                raise ValueError(
                    f"Unknown intake algae type: {action.get('intake algae type')}"
                )
        elif action.get("type") == "foul":
            match_statistics.foul.cnt += 1
        elif action.get("type") in [
            "start",
            "teleop start",
            "score coral",
            "score algae",
            "defense",
            "climb up",
            "give up",
        ]:
            pass
        else:
            raise ValueError(f"Unknown action type: {action.get('type')}")
    for action in teleop_actions:
        if action.get("type") == "intake coral":
            if action.get("intake coral type") in ["load station A", "load station B"]:
                match_statistics.intake_coral.teleop_load_station_cnt += 1
            elif action.get("intake coral type") == "ground":
                match_statistics.intake_coral.teleop_ground_cnt += 1
            elif action.get("intake coral type") == "fixed":
                match_statistics.intake_coral.teleop_fixed_cnt += 1
            else:
                raise ValueError(
                    f"Unknown intake coral type: {action.get('intake coral type')}"
                )
        elif action.get("type") == "intake algae":
            if action.get("intake algae type") == "ground":
                if action.get("ground algae source") == "front":
                    match_statistics.intake_algae.teleop_ground_front_cnt += 1
                elif action.get("ground algae source") == "middle":
                    match_statistics.intake_algae.teleop_ground_middle_cnt += 1
                elif action.get("ground algae source") == "back":
                    match_statistics.intake_algae.teleop_ground_back_cnt += 1
                else:
                    raise ValueError(
                        f"Unknown ground algae source: {action.get('ground algae source')}"
                    )
            elif action.get("intake algae type") == "reef":
                match_statistics.intake_algae.teleop_reef_cnt += 1
            elif action.get("intake algae type") == "scrape":
                match_statistics.intake_algae.teleop_scrape_cnt += 1
            else:
                raise ValueError(
                    f"Unknown intake algae type: {action.get('intake algae type')}"
                )
        elif action.get("type") == "foul":
            match_statistics.foul.cnt += 1
        elif action.get("type") in [
            "start",
            "teleop start",
            "score coral",
            "score algae",
            "defense",
            "climb up",
            "give up",
        ]:
            pass
        else:
            raise ValueError(f"Unknown action type: {action.get('type')}")


def process_cycle_statistics(
    match_statistics: MatchStatistics, time_slices: List[Dict[str, Any]]
):
    """
    处理周期统计
    """
    for time_slice in time_slices:
        if time_slice.get("type") == "score coral":
            match_statistics.score_coral.cycle_times.append(time_slice.get("duration"))
            match_statistics.score_coral.faces.append(time_slice.get("face"))
            if time_slice.get("success"):
                match_statistics.score_coral.successful_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            if time_slice.get("defended"):
                match_statistics.score_coral.defended_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            if time_slice.get("score coral type") == "L1":
                match_statistics.score_coral.l1_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            elif time_slice.get("score coral type") == "L2":
                match_statistics.score_coral.l2_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            elif time_slice.get("score coral type") == "L3":
                match_statistics.score_coral.l3_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            elif time_slice.get("score coral type") == "L4":
                match_statistics.score_coral.l4_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            elif time_slice.get("score coral type") == "Stack L1":
                match_statistics.score_coral.stack_l1_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )
            else:
                raise ValueError(
                    f"Unknown score coral type: {time_slice.get('score coral type')}"
                )
            if time_slice.get("timestamp") < 15000:
                match_statistics.score_coral.auto_index.add(
                    len(match_statistics.score_coral.cycle_times) - 1
                )

        elif time_slice.get("type") == "score algae":
            match_statistics.score_algae.cycle_times.append(time_slice.get("duration"))
            if time_slice.get("success"):
                match_statistics.score_algae.success_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
            if time_slice.get("defended"):
                match_statistics.score_algae.defended_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
            if time_slice.get("timestamp") < 15000:
                match_statistics.score_algae.auto_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
            if time_slice.get("score algae type") == "net":
                match_statistics.score_algae.place_net_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
            elif time_slice.get("score algae type") == "shooting":
                match_statistics.score_algae.shoot_net_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
            elif time_slice.get("score algae type") == "processor":
                match_statistics.score_algae.processor_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
                if time_slice.get("timestamp") > 144000:
                    match_statistics.score_algae.last_sec_processor_index.add(
                        len(match_statistics.score_algae.cycle_times) - 1
                    )
            elif time_slice.get("score algae type") == "tactical":
                match_statistics.score_algae.tactical_index.add(
                    len(match_statistics.score_algae.cycle_times) - 1
                )
            else:
                raise ValueError(
                    f"Unknown score algae type: {time_slice.get('score algae type')}"
                )
        elif time_slice.get("type") == "give up":
            match_statistics.give_up.cycle_times.append(time_slice.get("duration"))
        elif time_slice.get("type") == "defense":
            match_statistics.defense.cycle_times.append(time_slice.get("duration"))
        elif time_slice.get("type") == "climb up":
            match_statistics.climb_up.time = time_slice.get("timestamp")
            match_statistics.climb_up.duration = time_slice.get("duration")
            match_statistics.climb_up.status = time_slice.get("climb result")
        elif time_slice.get("type") == "teleop start":
            pass
        else:
            raise ValueError(f"Unknown action type: {time_slice.get('type')}")


def split_actions_by_phase(
    actions: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    根据阶段分割动作列表
    """
    auto_actions = []
    teleop_actions = []
    for action in actions:
        if action.get("timestamp") < 15000:
            auto_actions.append(action)
        else:
            teleop_actions.append(action)
    return auto_actions, teleop_actions


def _calculate_time_slices(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    根据Score类和Give Up和defense Action和climb up划分时间片

    Args:
        actions: 动作列表

    Returns:
        List[Dict]: 时间片结束的动作列表，每个动作额外附加了duration属性
    """
    if not actions:
        return []

    # 找到所有分界点action（Score类、Give Up、defense）
    boundary_actions = []

    for action in actions:
        action_type = action.get("type", "")
        if (
            action_type == "score coral"
            or action_type == "score algae"
            or action_type == "give up"
            or action_type == "defense"
            or action_type == "climb up"
            or action_type == "teleop start"  # todo: add this to frontend
        ):
            boundary_actions.append(action)

    if not boundary_actions:
        return []

    # 按时间排序
    boundary_actions.sort(key=lambda x: x.get("timestamp", 0))

    time_slices = []

    # 为每个boundary action创建时间片
    for i, current_action in enumerate(boundary_actions):
        current_timestamp = current_action.get("timestamp", 0)

        # 找到前一个boundary action的时间戳
        if i == 0:
            # 第一个action，从0开始
            prev_timestamp = 0
        else:
            prev_timestamp = boundary_actions[i - 1].get("timestamp", 0)

        # 计算时间片持续时间（转换为秒）
        duration = (current_timestamp - prev_timestamp) / 1000.0

        current_action["duration"] = duration
        time_slices.append(current_action)

    return time_slices


if __name__ == "__main__":
    import json

    with open(
        r"D:\work\frc\horus\backend\match_records\raw\match_record_SY_2910_Playoff_2_1751982952463.json",
        "r",
    ) as f:
        match_record = json.load(f)
    match_statistics = calculate_single_match_record_statistics(match_record)
    print(match_statistics)
