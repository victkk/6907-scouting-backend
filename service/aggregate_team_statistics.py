"""
从比赛统计数据聚合队伍统计数据的功能模块
"""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from dataclasses import fields
import statistics
from backend.schema.match_statistics_schema import MatchStatistics
from backend.schema.team_statistics_schema import (
    TeamStatistics,
    RankValue,
    RankValueMatch,
    MatchList,
    create_team_statistics,
    calculate_rank_data,
)


def create_team_statistics_from_matches(
    match_stats: List[MatchStatistics], filter_func: Optional[callable] = None
) -> List[TeamStatistics]:
    """
    从比赛统计数据列表创建队伍统计数据列表

    Args:
        match_stats: 比赛统计数据列表
        filter_func: 可选的过滤函数，返回True的比赛将被过滤掉

    Returns:
        队伍统计数据列表
    """
    # 按队伍号分组
    teams_matches = defaultdict(list)
    for match_stat in match_stats:
        if filter_func and filter_func(match_stat):
            continue

        teams_matches[match_stat.team_no].append(match_stat)

    # 为每个队伍创建统计数据
    team_statistics = []
    for team_no, matches in teams_matches.items():
        team_stat = _calculate_single_team_statistics(team_no, matches)
        team_statistics.append(team_stat)

    # 计算所有排名
    _calculate_all_rankings(team_statistics)

    return team_statistics


def _calculate_single_team_statistics(
    team_no: int, matches: List[MatchStatistics]
) -> TeamStatistics:
    """为单个队伍创建统计数据"""
    team_stat = create_team_statistics(team_no)
    if team_no == 2910:
        print(1)
    if not matches:
        return team_stat

    # 1. 计算时间占比数据
    _calculate_time_ratios(team_stat, matches)

    # 2. 计算爬升统计
    _calculate_climb_statistics(team_stat, matches)

    # 3. 计算BPS和EPA (目前先设为0，需要具体实现)
    _calculate_bps_epa_ppg(team_stat, matches)

    # 4. 计算自动阶段统计
    _calculate_auto_statistics(team_stat, matches)

    # 5. 计算手动筒统计
    _calculate_manual_coral_statistics(team_stat, matches)

    # 6. 计算手动球统计
    _calculate_manual_algae_statistics(team_stat, matches)

    # 7. 计算防守抗性统计
    _calculate_defense_resistance_statistics(team_stat, matches)

    return team_stat


def _calculate_time_ratios(
    team_stat: TeamStatistics, matches: List[MatchStatistics]
) -> None:
    """计算时间占比数据"""
    total_coral_time = 0.0
    total_algae_time = 0.0
    total_defense_time = 0.0
    total_give_up_time = 0.0

    for match in matches:
        total_coral_time += match.get_coral_teleop_time()
        total_algae_time += match.get_algae_teleop_time()
        total_defense_time += match.get_defense_total_time()
        total_give_up_time += match.get_give_up_total_time()

    # 计算平均时间占比（相对于135秒）
    num_matches = len(matches)
    team_stat.cycle_teleop_coral_time_ratio.value = (
        total_coral_time / num_matches
    ) / 135.0
    team_stat.cycle_teleop_algae_time_ratio.value = (
        total_algae_time / num_matches
    ) / 135.0
    team_stat.cycle_teleop_defense_time_ratio.value = (
        total_defense_time / num_matches
    ) / 135.0
    team_stat.cycle_teleop_give_up_time_ratio.value = (
        total_give_up_time / num_matches
    ) / 135.0


def _calculate_climb_statistics(
    team_stat: TeamStatistics, matches: List[MatchStatistics]
) -> None:
    """计算爬升统计数据"""
    success_match_nos = []
    fail_match_nos = []
    touch_chain_match_nos = []
    success_tournament_levels = []
    fail_tournament_levels = []
    touch_chain_tournament_levels = []
    climb_times = []
    park_times = []
    for match in matches:
        if match.climb_up.status in ["success", "fail", "touch_chain", "park"]:
            park_times.append(match.climb_up.time / 1000)
        if match.climb_up.status == "success":
            success_match_nos.append(match.match_no)
            success_tournament_levels.append(match.tournament_level)
            if match.climb_up.duration > 0:
                climb_times.append(match.climb_up.duration)
            else:
                climb_times.append(151)
        elif match.climb_up.status == "fail":
            fail_match_nos.append(match.match_no)
            fail_tournament_levels.append(match.tournament_level)
        elif match.climb_up.status == "touch_chain":
            touch_chain_match_nos.append(match.match_no)
            touch_chain_tournament_levels.append(match.tournament_level)

    # 设置场次数据
    team_stat.climb_success_matches.match_nos = success_match_nos
    team_stat.climb_success_matches.tournament_levels = success_tournament_levels
    team_stat.climb_fail_matches.match_nos = fail_match_nos
    team_stat.climb_fail_matches.tournament_levels = fail_tournament_levels
    team_stat.climb_touch_chain_matches.match_nos = touch_chain_match_nos
    team_stat.climb_touch_chain_matches.tournament_levels = (
        touch_chain_tournament_levels
    )
    if park_times:
        team_stat.climb_park_time_median.value = statistics.median(park_times)
    else:
        team_stat.climb_park_time_median.value = 150.0
    # 计算成功率
    total_attempts = (
        len(success_match_nos) + len(fail_match_nos) + len(touch_chain_match_nos)
    )
    if total_attempts > 0:
        team_stat.climb_success_percentage.value = (
            len(success_match_nos) / total_attempts
        )
    else:
        team_stat.climb_success_percentage.value = 0.0

    # 计算最短爬升时间
    if climb_times:
        min_time = min(climb_times)
        min_index = climb_times.index(min_time)
        team_stat.climb_success_cycle_time_min.value = min_time
        team_stat.climb_success_cycle_time_min.match_no = success_match_nos[min_index]
        team_stat.climb_success_cycle_time_min.tournament_level = (
            success_tournament_levels[min_index]
        )
    else:
        team_stat.climb_success_cycle_time_min.value = 151.0


def _calculate_bps_epa_ppg(
    team_stat: TeamStatistics, matches: List[MatchStatistics]
) -> None:

    total_branches = 0
    total_branch_time = 0
    total_epas = 0
    ppg = []
    for match in matches:
        total_branches += len(
            match.score_coral.successful_index
            & (
                match.score_coral.l2_index
                | match.score_coral.l3_index
                | match.score_coral.l4_index
            )
        )
        total_branch_time += sum(
            match.score_coral.cycle_times[index]
            for index in (
                match.score_coral.l2_index
                | match.score_coral.l3_index
                | match.score_coral.l4_index
            )
        )
        # 自动： leave*3 高中筒*2 低筒*1
        total_epas += match.leave * 3
        total_epas += (
            len(
                match.score_coral.successful_index
                & match.score_coral.auto_index
                & (match.score_coral.l3_index | match.score_coral.l4_index)
            )
            * 2
            + len(
                match.score_coral.successful_index
                & match.score_coral.auto_index
                & (
                    match.score_coral.l1_index
                    | match.score_coral.l2_index
                    | match.score_coral.stack_l1_index
                )
            )
            * 1
        )
        # 手动： 槽筒*2
        total_epas += (
            len(
                (
                    match.score_coral.successful_index
                    & (match.score_coral.stack_l1_index | match.score_coral.l1_index)
                )
                - match.score_coral.auto_index
            )
            * 2
        )
        # 藻类： 处理器*2 网*4 处理器*2 压哨*2
        total_epas += (
            len(match.score_algae.success_index & match.score_algae.processor_index) * 2
            + len(match.score_algae.success_index & match.score_algae.place_net_index)
            * 4
            + len(match.score_algae.success_index & match.score_algae.shoot_net_index)
            * 4
            + len(
                match.score_algae.success_index
                & match.score_algae.last_sec_processor_index
            )
            * 2
        )
        # 爬升： 成功*10
        total_epas += 10 if match.climb_up.status == "success" else 0
        points = 0
        points += 3 if match.leave else 0
        points += (
            len(
                match.score_coral.successful_index
                & (match.score_coral.l1_index | match.score_coral.stack_l1_index)
            )
            * 2
        ) + len(
            match.score_coral.successful_index
            & (match.score_coral.l1_index | match.score_coral.stack_l1_index)
            & match.score_coral.auto_index
        )
        points += (
            len(match.score_coral.successful_index & match.score_coral.l2_index) * 3
        ) + len(
            match.score_coral.successful_index
            & match.score_coral.l2_index
            & match.score_coral.auto_index
        )
        points += (
            len(match.score_coral.successful_index & match.score_coral.l3_index) * 4
        ) + len(
            match.score_coral.successful_index
            & match.score_coral.l3_index
            & match.score_coral.auto_index
        ) * 2
        points += (
            len(match.score_coral.successful_index & match.score_coral.l4_index) * 5
        ) + len(
            match.score_coral.successful_index
            & match.score_coral.l4_index
            & match.score_coral.auto_index
        ) * 2
        points += (
            len(match.score_algae.success_index & match.score_algae.processor_index) * 6
        )
        points += (
            len(
                match.score_algae.success_index
                & (
                    match.score_algae.place_net_index
                    | match.score_algae.shoot_net_index
                )
            )
            * 4
        )
        points += 12 if match.climb_up.status == "success" else 0
        points += 2 if match.climb_up.status == "park" else 0
        ppg.append(points)

    team_stat.bps_value.value = (
        total_branches / total_branch_time if total_branch_time > 0 else 0
    )
    team_stat.epa_value.value = total_epas / len(matches)
    team_stat.ppg_avg.value = statistics.mean(ppg)
    team_stat.ppg_max_single_match.value = max(ppg)
    team_stat.ppg_max_single_match.match_no = matches[ppg.index(max(ppg))].match_no
    team_stat.ppg_max_single_match.tournament_level = matches[
        ppg.index(max(ppg))
    ].tournament_level


def _calculate_auto_statistics(
    team_stat: TeamStatistics, matches: List[MatchStatistics]
) -> None:
    """计算自动阶段统计数据"""
    line_cross_count = 0
    preload_coral_count = 0
    high_mid_coral_counts = []
    low_slot_coral_counts = []
    net_place_counts = []
    algae_process_counts = []
    total_success_high_mid_cnt = 0
    total_high_mid_cnt = 0
    total_success_low_slot_cnt = 0
    total_low_slot_cnt = 0
    total_success_net_place_cnt = 0
    total_net_place_cnt = 0
    total_success_algae_process_cnt = 0
    total_algae_process_cnt = 0
    leave_cnt = 0
    for match in matches:
        leave_cnt += 1 if match.leave else 0
        preload_coral_count += (
            1
            if 0 in (match.score_coral.successful_index & match.score_coral.auto_index)
            else 0
        )
        # 自动高中筒统计
        success_high_mid_count = len(
            match.score_coral.successful_index
            & match.score_coral.auto_index
            & (match.score_coral.l3_index | match.score_coral.l4_index)
        )
        total_high_mid_cnt += len(
            match.score_coral.auto_index
            & (match.score_coral.l3_index | match.score_coral.l4_index)
        )
        total_success_high_mid_cnt += success_high_mid_count
        if success_high_mid_count > 0:
            high_mid_coral_counts.append(
                (success_high_mid_count, match.match_no, match.tournament_level)
            )

        # 自动低筒槽筒统计
        success_low_slot_count = len(
            match.score_coral.successful_index
            & match.score_coral.auto_index
            & (
                match.score_coral.stack_l1_index
                | match.score_coral.l1_index
                | match.score_coral.l2_index
            )
        )
        total_low_slot_cnt += len(
            match.score_coral.auto_index
            & (match.score_coral.l1_index | match.score_coral.stack_l1_index)
        )
        total_success_low_slot_cnt += success_low_slot_count
        if success_low_slot_count > 0:
            low_slot_coral_counts.append(
                (success_low_slot_count, match.match_no, match.tournament_level)
            )

        # 自动网投统计
        success_net_place_count = len(
            match.score_algae.success_index
            & match.score_algae.auto_index
            & (match.score_algae.place_net_index | match.score_algae.shoot_net_index)
        )
        total_net_place_cnt += len(
            match.score_algae.auto_index
            & (match.score_algae.place_net_index | match.score_algae.shoot_net_index)
        )
        total_success_net_place_cnt += success_net_place_count
        if success_net_place_count > 0:
            net_place_counts.append(
                (success_net_place_count, match.match_no, match.tournament_level)
            )

        # 自动藻类处理统计
        algae_process_count = (
            match.intake_algae.auto_reef_cnt + match.intake_algae.auto_scrape_cnt
        )
        if algae_process_count > 0:
            algae_process_counts.append(
                (algae_process_count, match.match_no, match.tournament_level)
            )
    team_stat.auto_line_cross_percentage.value = leave_cnt / len(matches)
    team_stat.auto_high_mid_coral_success_rate.value = (
        total_success_high_mid_cnt / total_high_mid_cnt
        if total_high_mid_cnt > 0
        else 0.0
    )
    team_stat.auto_low_slot_coral_success_rate.value = (
        total_success_low_slot_cnt / total_low_slot_cnt
        if total_low_slot_cnt > 0
        else 0.0
    )

    # 计算最大值和场次
    if high_mid_coral_counts:
        max_count, match_no, tournament_level = max(
            high_mid_coral_counts, key=lambda x: x[0]
        )
        team_stat.auto_high_mid_coral_max.value = max_count
        team_stat.auto_high_mid_coral_max.match_no = match_no
        team_stat.auto_high_mid_coral_max.tournament_level = tournament_level

    if low_slot_coral_counts:
        max_count, match_no, tournament_level = max(
            low_slot_coral_counts, key=lambda x: x[0]
        )
        team_stat.auto_low_slot_coral_max.value = max_count
        team_stat.auto_low_slot_coral_max.match_no = match_no
        team_stat.auto_low_slot_coral_max.tournament_level = tournament_level

    if net_place_counts:
        max_count, match_no, tournament_level = max(
            net_place_counts, key=lambda x: x[0]
        )
        team_stat.auto_net_place_max.value = max_count
        team_stat.auto_net_place_max.match_no = match_no
        team_stat.auto_net_place_max.tournament_level = tournament_level

    if algae_process_counts:
        max_count, match_no, tournament_level = max(
            algae_process_counts, key=lambda x: x[0]
        )
        team_stat.auto_algae_process_max.value = max_count
        team_stat.auto_algae_process_max.match_no = match_no
        team_stat.auto_algae_process_max.tournament_level = tournament_level
    team_stat.auto_preload_coral_percentage.value = preload_coral_count / len(matches)


def _calculate_manual_coral_statistics(
    team_stat: TeamStatistics, matches: List[MatchStatistics]
) -> None:
    """计算手动筒统计数据"""
    l1_undefended_cycle_times = []
    l2_undefended_cycle_times = []
    l3_undefended_cycle_times = []
    l4_undefended_cycle_times = []
    stack_l1_undefended_cycle_times = []

    l1_success_counts = []
    l2_success_counts = []
    l3_success_counts = []
    l4_success_counts = []
    stack_l1_success_counts = []

    l1_attempt_counts = []
    l2_attempt_counts = []
    l3_attempt_counts = []
    l4_attempt_counts = []
    stack_l1_attempt_counts = []
    match_nos = []
    tournament_levels = []
    coral_source_ground_cnt = 0
    coral_source_loading_station_cnt = 0
    for match in matches:
        coral_source_ground_cnt += match.intake_coral.teleop_ground_cnt
        coral_source_loading_station_cnt += match.intake_coral.teleop_load_station_cnt
        l1_success_counts.append(
            len(
                match.score_coral.successful_index
                & match.score_coral.l1_index - match.score_coral.auto_index
            )
        )
        l1_attempt_counts.append(
            len(match.score_coral.l1_index - match.score_coral.auto_index)
        )

        l2_success_counts.append(
            len(
                match.score_coral.successful_index
                & match.score_coral.l2_index - match.score_coral.auto_index
            )
        )
        l2_attempt_counts.append(
            len(match.score_coral.l2_index - match.score_coral.auto_index)
        )
        l3_success_counts.append(
            len(
                match.score_coral.successful_index
                & match.score_coral.l3_index - match.score_coral.auto_index
            )
        )
        l3_attempt_counts.append(
            len(match.score_coral.l3_index - match.score_coral.auto_index)
        )
        l4_success_counts.append(
            len(
                match.score_coral.successful_index
                & match.score_coral.l4_index - match.score_coral.auto_index
            )
        )
        l4_attempt_counts.append(
            len(match.score_coral.l4_index - match.score_coral.auto_index)
        )
        stack_l1_success_counts.append(
            len(
                match.score_coral.successful_index
                & match.score_coral.stack_l1_index - match.score_coral.auto_index
            )
        )
        stack_l1_attempt_counts.append(
            len(match.score_coral.stack_l1_index - match.score_coral.auto_index)
        )
        match_nos.append(match.match_no)
        tournament_levels.append(match.tournament_level)

        # cycle time
        l1_undefended_cycle_times.append(
            [
                match.score_coral.cycle_times[index]
                for index in (
                    match.score_coral.successful_index
                    & match.score_coral.l1_index
                    - match.score_coral.auto_index
                    - match.score_coral.defended_index
                )
            ]
        )
        l2_undefended_cycle_times.append(
            [
                match.score_coral.cycle_times[index]
                for index in (
                    match.score_coral.successful_index
                    & match.score_coral.l2_index
                    - match.score_coral.auto_index
                    - match.score_coral.defended_index
                )
            ]
        )
        l3_undefended_cycle_times.append(
            [
                match.score_coral.cycle_times[index]
                for index in (
                    match.score_coral.successful_index
                    & match.score_coral.l3_index
                    - match.score_coral.auto_index
                    - match.score_coral.defended_index
                )
            ]
        )
        l4_undefended_cycle_times.append(
            [
                match.score_coral.cycle_times[index]
                for index in (
                    match.score_coral.successful_index
                    & match.score_coral.l4_index
                    - match.score_coral.auto_index
                    - match.score_coral.defended_index
                )
            ]
        )
        stack_l1_undefended_cycle_times.append(
            [
                match.score_coral.cycle_times[index]
                for index in (
                    match.score_coral.successful_index
                    & match.score_coral.stack_l1_index
                    - match.score_coral.auto_index
                    - match.score_coral.defended_index
                )
            ]
        )

    # 展平嵌套列表
    l1_undefended_cycle_times_flat = [
        time for match_times in l1_undefended_cycle_times for time in match_times
    ]
    l2_undefended_cycle_times_flat = [
        time for match_times in l2_undefended_cycle_times for time in match_times
    ]
    l3_undefended_cycle_times_flat = [
        time for match_times in l3_undefended_cycle_times for time in match_times
    ]
    l4_undefended_cycle_times_flat = [
        time for match_times in l4_undefended_cycle_times for time in match_times
    ]
    stack_l1_undefended_cycle_times_flat = [
        time for match_times in stack_l1_undefended_cycle_times for time in match_times
    ]

    all_undefended_cycle_times_flat = (
        l1_undefended_cycle_times_flat
        + l2_undefended_cycle_times_flat
        + l3_undefended_cycle_times_flat
        + l4_undefended_cycle_times_flat
        + stack_l1_undefended_cycle_times_flat
    )

    team_stat.l1_teleop_success_count_avg.value = statistics.mean(l1_success_counts)
    team_stat.l1_teleop_success_percentage.value = (
        statistics.mean(l1_success_counts) / statistics.mean(l1_attempt_counts)
        if statistics.mean(l1_attempt_counts) > 0
        else 0
    )
    team_stat.l1_teleop_undefended_success_cycle_time_median.value = (
        statistics.median(l1_undefended_cycle_times_flat)
        if l1_undefended_cycle_times_flat
        else 9999.0
    )

    team_stat.l2_teleop_success_count_avg.value = statistics.mean(l2_success_counts)
    team_stat.l2_teleop_success_percentage.value = (
        statistics.mean(l2_success_counts) / statistics.mean(l2_attempt_counts)
        if statistics.mean(l2_attempt_counts) > 0
        else 0
    )
    team_stat.l2_teleop_undefended_success_cycle_time_median.value = (
        statistics.median(l2_undefended_cycle_times_flat)
        if l2_undefended_cycle_times_flat
        else 9999.0
    )

    team_stat.l3_teleop_success_count_avg.value = statistics.mean(l3_success_counts)
    team_stat.l3_teleop_success_percentage.value = (
        statistics.mean(l3_success_counts) / statistics.mean(l3_attempt_counts)
        if statistics.mean(l3_attempt_counts) > 0
        else 0.0
    )
    team_stat.l3_teleop_undefended_success_cycle_time_median.value = (
        statistics.median(l3_undefended_cycle_times_flat)
        if l3_undefended_cycle_times_flat
        else 9999.0
    )

    team_stat.l4_teleop_success_count_avg.value = statistics.mean(l4_success_counts)
    team_stat.l4_teleop_success_percentage.value = (
        statistics.mean(l4_success_counts) / statistics.mean(l4_attempt_counts)
        if statistics.mean(l4_attempt_counts) > 0
        else 0
    )
    team_stat.l4_teleop_undefended_success_cycle_time_median.value = (
        statistics.median(l4_undefended_cycle_times_flat)
        if l4_undefended_cycle_times_flat
        else 9999.0
    )

    team_stat.stack_l1_teleop_success_count_avg.value = statistics.mean(
        stack_l1_success_counts
    )
    team_stat.stack_l1_teleop_success_percentage.value = (
        statistics.mean(stack_l1_success_counts)
        / statistics.mean(stack_l1_attempt_counts)
        if statistics.mean(stack_l1_attempt_counts) > 0
        else 0
    )
    team_stat.stack_l1_teleop_undefended_success_cycle_time_median.value = (
        statistics.median(stack_l1_undefended_cycle_times_flat)
        if stack_l1_undefended_cycle_times_flat
        else 9999.0
    )

    all_success_counts = [
        l1 + l2 + l3 + l4 + stack_l1
        for l1, l2, l3, l4, stack_l1 in zip(
            l1_success_counts,
            l2_success_counts,
            l3_success_counts,
            l4_success_counts,
            stack_l1_success_counts,
        )
    ]
    all_attempt_counts = [
        l1 + l2 + l3 + l4 + stack_l1
        for l1, l2, l3, l4, stack_l1 in zip(
            l1_attempt_counts,
            l2_attempt_counts,
            l3_attempt_counts,
            l4_attempt_counts,
            stack_l1_attempt_counts,
        )
    ]

    team_stat.total_teleop_success_count_avg.value = statistics.mean(all_success_counts)
    team_stat.total_teleop_undefended_success_cycle_time_median.value = (
        statistics.median(all_undefended_cycle_times_flat)
        if all_undefended_cycle_times_flat
        else 9999.0
    )
    team_stat.total_teleop_success_percentage.value = (
        statistics.mean(all_success_counts) / statistics.mean(all_attempt_counts)
        if statistics.mean(all_attempt_counts) > 0
        else 0
    )
    team_stat.coral_source_ground_percentage.value = (
        coral_source_ground_cnt
        / (coral_source_loading_station_cnt + coral_source_ground_cnt)
        if (coral_source_loading_station_cnt + coral_source_ground_cnt)
        else 0
    )
    team_stat.coral_source_station_percentage = (
        coral_source_loading_station_cnt
        / (coral_source_loading_station_cnt + coral_source_ground_cnt)
        if (coral_source_loading_station_cnt + coral_source_ground_cnt)
        else 0.0
    )


def _calculate_manual_algae_statistics(
    team_stat: TeamStatistics, matches: List[MatchStatistics]
) -> None:
    """计算手动球统计数据"""
    scrape_cnt = []
    pickup_cnt = []
    cycle_success_cnt = []
    front_cnt = 0
    middle_cnt = 0
    back_cnt = 0
    reef_cnt = 0
    shoot_net_cnt = 0
    place_net_cnt = 0
    shoot_net_success_cnt = 0
    place_net_success_cnt = 0
    tactical_cnt = []
    net_success_undefended_cycle_times = []

    last_second_processor_matchnos = []
    last_second_processor_tournament_levels = []
    max_processor_cnt = 0
    for match in matches:
        scrape_cnt.append(match.intake_algae.teleop_scrape_cnt)
        pickup_cnt.append(match.intake_algae.teleop_reef_cnt)
        cycle_success_cnt.append(
            len(match.score_algae.success_index - match.score_algae.auto_index)
        )
        front_cnt += match.intake_algae.teleop_ground_front_cnt
        middle_cnt += match.intake_algae.teleop_ground_middle_cnt
        back_cnt += match.intake_algae.teleop_ground_back_cnt
        reef_cnt += match.intake_algae.teleop_reef_cnt
        shoot_net_cnt += len(match.score_algae.shoot_net_index)
        place_net_cnt += len(match.score_algae.place_net_index)
        shoot_net_success_cnt += len(
            match.score_algae.success_index & match.score_algae.shoot_net_index
        )
        place_net_success_cnt += len(
            match.score_algae.success_index & match.score_algae.place_net_index
        )
        net_success_undefended_cycle_times.append(
            [
                match.score_algae.cycle_times[index]
                for index in (
                    match.score_algae.success_index
                    & (
                        match.score_algae.place_net_index
                        | match.score_algae.shoot_net_index
                    )
                    - match.score_algae.defended_index
                )
            ]
        )
        tactical_cnt.append(len(match.score_algae.tactical_index))
        if match.score_algae.last_sec_processor_index & match.score_algae.success_index:
            last_second_processor_matchnos.append(match.match_no)
            last_second_processor_tournament_levels.append(match.tournament_level)
        if len(match.score_algae.processor_index) > max_processor_cnt:
            max_processor_cnt = len(match.score_algae.processor_index)
            max_processor_matchnos = match.match_no
            max_processor_tournament_levels = match.tournament_level
    # 展平嵌套列表
    net_success_undefended_cycle_times_flat = [
        time
        for match_times in net_success_undefended_cycle_times
        for time in match_times
    ]
    team_stat.processor_success_max_single_match.value = max_processor_cnt
    if max_processor_cnt > 0:
        team_stat.processor_success_max_single_match.match_no = max_processor_matchnos
        team_stat.processor_success_max_single_match.tournament_level = (
            max_processor_tournament_levels
        )

    team_stat.avg_scrape_algae_count.value = statistics.mean(scrape_cnt)
    team_stat.avg_pickup_algae_count.value = statistics.mean(pickup_cnt)
    team_stat.algae_success_cycle_count_median.value = statistics.median(
        cycle_success_cnt
    )

    team_stat.algae_success_cycle_count_max.value = max(cycle_success_cnt)
    team_stat.algae_success_cycle_count_max.match_no = matches[
        cycle_success_cnt.index(max(cycle_success_cnt))
    ].match_no
    team_stat.algae_success_cycle_count_max.tournament_level = matches[
        cycle_success_cnt.index(max(cycle_success_cnt))
    ].tournament_level

    total_algae_sources = front_cnt + middle_cnt + back_cnt + reef_cnt
    if total_algae_sources > 0:
        team_stat.algae_source_front_percentage.value = front_cnt / total_algae_sources
        team_stat.algae_source_mid_percentage.value = middle_cnt / total_algae_sources
        team_stat.algae_source_back_percentage.value = back_cnt / total_algae_sources
        team_stat.algae_source_reef_percentage.value = reef_cnt / total_algae_sources
    else:
        team_stat.algae_source_front_percentage.value = 0.0
        team_stat.algae_source_mid_percentage.value = 0.0
        team_stat.algae_source_back_percentage.value = 0.0
        team_stat.algae_source_reef_percentage.value = 0.0

    total_net_attempts = place_net_cnt + shoot_net_cnt
    if total_net_attempts > 0:
        team_stat.net_place_percentage.value = place_net_cnt / total_net_attempts
        team_stat.net_shoot_percentage.value = shoot_net_cnt / total_net_attempts
    else:
        team_stat.net_place_percentage.value = 0.0
        team_stat.net_shoot_percentage.value = 0.0

    team_stat.net_place_success_rate.value = (
        place_net_success_cnt / place_net_cnt if place_net_cnt > 0 else 0.0
    )
    team_stat.net_shoot_success_rate.value = (
        shoot_net_success_cnt / shoot_net_cnt if shoot_net_cnt > 0 else 0.0
    )
    team_stat.net_success_undefended_cycle_time_median.value = (
        statistics.median(net_success_undefended_cycle_times_flat)
        if net_success_undefended_cycle_times_flat
        else 9999.0
    )
    team_stat.tactical_max_single_match.value = max(tactical_cnt)
    team_stat.tactical_max_single_match.match_no = matches[
        tactical_cnt.index(max(tactical_cnt))
    ].match_no
    team_stat.tactical_max_single_match.tournament_level = matches[
        tactical_cnt.index(max(tactical_cnt))
    ].tournament_level
    team_stat.last_second_processer_matches.match_nos = last_second_processor_matchnos
    team_stat.last_second_processer_matches.tournament_levels = (
        last_second_processor_tournament_levels
    )


def _calculate_defense_resistance_statistics(
    team_stat: "TeamStatistics", matches: List["MatchStatistics"]
) -> None:
    """计算防守抗性统计数据（已修复）"""
    total_successful_coral_cycles = 0
    defended_coral_cycles = 0
    undefended_coral_cycles = 0

    # 更改：列表将存储 (时间, 比赛) 元组
    defended_cycle_times_with_match = []
    undefended_cycle_times = []
    defended_counts_by_match = []

    for match in matches:
        # 计算手动阶段的筒统计
        teleop_indices = (
            set(range(len(match.score_coral.cycle_times)))
            - match.score_coral.auto_index
        )
        teleop_success_indices = teleop_indices & match.score_coral.successful_index
        teleop_defended_indices = teleop_indices & match.score_coral.defended_index
        teleop_undefended_indices = teleop_indices - match.score_coral.defended_index

        total_successful_coral_cycles += len(teleop_success_indices)
        defended_coral_cycles += len(teleop_defended_indices)
        undefended_coral_cycles += len(teleop_undefended_indices)
        defended_count = len(teleop_defended_indices)

        defended_counts_by_match.append(defended_count)

        # 修复：收集cycle时间时，附带比赛信息
        for idx in teleop_defended_indices & match.score_coral.successful_index:
            cycle_time = match.score_coral.cycle_times[idx]
            defended_cycle_times_with_match.append((cycle_time, match))

        for idx in teleop_undefended_indices & match.score_coral.successful_index:
            undefended_cycle_times.append(match.score_coral.cycle_times[idx])

    # 计算被防守百分比
    if total_successful_coral_cycles > 0:
        team_stat.coral_defended_percentage.value = defended_coral_cycles / (
            defended_coral_cycles + undefended_coral_cycles
        )
    else:
        team_stat.coral_defended_percentage.value = 0.0

    # 计算单场最大被防守数 (这部分逻辑原本就是正确的)
    if defended_counts_by_match:
        max_defended_count = max(defended_counts_by_match)
        max_index = defended_counts_by_match.index(max_defended_count)
        team_stat.coral_defended_max_single_match.value = max_defended_count
        team_stat.coral_defended_max_single_match.match_no = matches[max_index].match_no
        team_stat.coral_defended_max_single_match.tournament_level = matches[
            max_index
        ].tournament_level
    else:
        team_stat.coral_defended_max_single_match.value = 0.0

    # 修复：计算被防守时的最大和中位数周期时间
    if defended_cycle_times_with_match:
        # 使用 key 参数在元组列表中找到最大值
        max_time_tuple = max(defended_cycle_times_with_match, key=lambda item: item[0])
        match_with_max_time = max_time_tuple[1]

        team_stat.defended_success_coral_cycle_time_max.value = max_time_tuple[0]
        team_stat.defended_success_coral_cycle_time_max.match_no = (
            match_with_max_time.match_no
        )
        team_stat.defended_success_coral_cycle_time_max.tournament_level = (
            match_with_max_time.tournament_level
        )

        # 为了计算中位数，先提取所有时间值
        defended_times = [item[0] for item in defended_cycle_times_with_match]
        team_stat.defended_success_coral_cycle_time_median.value = statistics.median(
            defended_times
        )
    else:
        team_stat.defended_success_coral_cycle_time_max.value = 9999.0
        team_stat.defended_success_coral_cycle_time_median.value = 9999.0

    if undefended_cycle_times:
        team_stat.undefended_success_coral_cycle_time_median.value = statistics.median(
            undefended_cycle_times
        )
    else:
        team_stat.undefended_success_coral_cycle_time_median.value = 9999.0

    # 修复：计算被防守vs无防守的时间增加百分比
    if defended_cycle_times_with_match and undefended_cycle_times:
        # 同样，先提取时间值再计算中位数
        defended_times = [item[0] for item in defended_cycle_times_with_match]
        defended_median = statistics.median(defended_times)
        undefended_median = statistics.median(undefended_cycle_times)

        if undefended_median > 0:
            increase_percentage = (
                defended_median - undefended_median
            ) / undefended_median
            team_stat.defended_vs_undefended_success_coral_cycle_time_increase_percentage.value = (
                increase_percentage
            )
        else:
            team_stat.defended_vs_undefended_success_coral_cycle_time_increase_percentage.value = (
                0.0
            )
    else:
        team_stat.defended_vs_undefended_success_coral_cycle_time_increase_percentage.value = (
            0.0
        )


def _calculate_all_rankings(team_statistics: List[TeamStatistics]) -> None:
    """计算所有需要排名的字段"""
    # 需要排名的字段列表 (字段名, 是否降序)
    ranking_fields_dict = defaultdict(bool)
    ranking_fields_dict.update(
        {
            "cycle_teleop_coral_time_ratio": True,
            "cycle_teleop_algae_time_ratio": True,
            "cycle_teleop_defense_time_ratio": True,
            "cycle_teleop_give_up_time_ratio": False,
            "climb_success_percentage": True,
            "climb_park_time_median": False,
            "bps_value": True,
            "epa_value": True,
            "auto_line_cross_percentage": True,
            "auto_high_mid_coral_success_rate": True,
            "auto_low_slot_coral_success_rate": True,
            "auto_high_mid_coral_max": True,
            "auto_low_slot_coral_max": True,
            "auto_net_place_max": True,
            "auto_algae_process_max": True,
            "l1_teleop_success_count_avg": True,
            "l1_teleop_success_percentage": True,
            "l1_teleop_undefended_success_cycle_time_median": False,
            "l2_teleop_success_count_avg": True,
            "l2_teleop_success_percentage": True,
            "l2_teleop_undefended_success_cycle_time_median": False,
            "l3_teleop_success_count_avg": True,
            "l3_teleop_success_percentage": True,
            "l3_teleop_undefended_success_cycle_time_median": False,
            "l4_teleop_success_count_avg": True,
            "l4_teleop_success_percentage": True,
            "l4_teleop_undefended_success_cycle_time_median": False,
            "stack_l1_teleop_success_count_avg": True,
            "stack_l1_teleop_success_percentage": True,
            "stack_l1_teleop_undefended_success_cycle_time_median": False,
            "total_teleop_success_count_avg": True,
            "total_teleop_success_percentage": True,
            "total_teleop_undefended_success_cycle_time_median": False,
            "avg_scrape_algae_count": True,
            "avg_pickup_algae_count": True,
            "algae_success_cycle_count_median": True,
            "net_success_undefended_cycle_time_median": False,
            "net_place_success_rate": True,
            "net_shoot_success_rate": True,
            "coral_defended_percentage": True,
            "defended_success_coral_cycle_time_median": False,
            "undefended_success_coral_cycle_time_median": False,
            "defended_vs_undefended_success_coral_cycle_time_increase_percentage": False,
            "ppg_avg": True,
            "ppg_max_single_match": True,
            "climb_success_cycle_time_min": False,
            "climb_success_cycle_time_max": False,
            "climb_success_cycle_time_median": False,
            "climb_success_cycle_time_avg": False,
            "climb_success_cycle_time_std": False,
            "climb_success_cycle_time_min_match": False,
            "algae_source_front_percentage": True,
            "algae_source_mid_percentage": True,
            "algae_source_back_percentage": True,
            "algae_source_reef_percentage": True,
            "net_place_percentage": True,
            "net_shoot_percentage": True,
            "tactical_max_single_match": True,
            "last_second_processer_matches": True,
            "auto_preload_coral_percentage": True,
        }
    )
    # 计算每个字段的排名
    for field in fields(TeamStatistics):
        try:

            field_name = field.name
            if field.type in [RankValue, RankValueMatch]:
                descending = ranking_fields_dict[field_name]
                calculate_rank_data(team_statistics, field_name, descending)

        except AttributeError:
            # 如果字段不存在，跳过该字段的排名计算
            print(
                f"Warning: Field '{field_name}' not found in TeamStatistics, skipping ranking calculation"
            )
            continue


# 使用示例
if __name__ == "__main__":
    import sys
    import os
    import json

    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from backend.schema.match_statistics_schema import MatchStatistics

    def safe_print(label, value, format_str="{:.1f}", unit="", show_rank=True):
        """安全打印数值，处理可能的错误"""
        try:
            if hasattr(value, "value"):
                val = value.value
            else:
                val = value

            if show_rank and hasattr(value, "rank") and value.rank > 0:
                print(f"{label}: {format_str.format(val)}{unit} (排名: {value.rank})")
            else:
                print(f"{label}: {format_str.format(val)}{unit}")
        except (AttributeError, TypeError, ValueError) as e:
            print(f"{label}: 数据错误 - {e}")

    def print_match_list(label, match_list):
        """打印场次列表"""
        try:
            if hasattr(match_list, "match_nos") and hasattr(
                match_list, "tournament_levels"
            ):
                if match_list.match_nos:
                    matches_info = [
                        f"{no}({level})"
                        for no, level in zip(
                            match_list.match_nos, match_list.tournament_levels
                        )
                    ]
                    print(f"{label}: {', '.join(matches_info)}")
                else:
                    print(f"{label}: 无")
            else:
                print(f"{label}: 数据格式错误")
        except Exception as e:
            print(f"{label}: 打印错误 - {e}")

    # 检查数据目录
    processed_dir = "backend/match_records/processed"
    if not os.path.exists(processed_dir):
        print(f"错误: 目录 '{processed_dir}' 不存在")
        print("请确保已经有处理过的比赛数据文件")
        exit(1)

    # 加载比赛数据
    match_stats = []
    json_files = [f for f in os.listdir(processed_dir) if f.endswith(".json")]

    if not json_files:
        print(f"错误: 在 '{processed_dir}' 目录中未找到任何JSON文件")
        exit(1)

    print(f"找到 {len(json_files)} 个比赛数据文件")

    for file in json_files:
        try:
            match_stat = MatchStatistics.from_json_file(f"{processed_dir}/{file}")
            match_stats.append(match_stat)
            print(f"成功加载: {file}")
        except Exception as e:
            print(f"加载失败 {file}: {e}")

    if not match_stats:
        print("错误: 没有成功加载任何比赛数据")
        exit(1)

    print(f"\n总共加载了 {len(match_stats)} 场比赛数据")

    # 创建队伍统计
    try:
        team_stats = create_team_statistics_from_matches(match_stats)
        print(f"成功创建了 {len(team_stats)} 个队伍的统计数据")
    except Exception as e:
        print(f"创建队伍统计数据失败: {e}")
        exit(1)

    # 输出结果
    for team_stat in team_stats:
        print(f"\n{'='*50}")
        print(f"队伍 {team_stat.team_no} 统计数据")
        print(f"{'='*50}")

        # 基本时间分配
        print("\n--- 时间分配 ---")
        safe_print("筒时间占比", team_stat.cycle_teleop_coral_time_ratio, "{:.2%}")
        safe_print("球时间占比", team_stat.cycle_teleop_algae_time_ratio, "{:.2%}")
        safe_print("防守时间占比", team_stat.cycle_teleop_defense_time_ratio, "{:.2%}")
        safe_print("放弃时间占比", team_stat.cycle_teleop_give_up_time_ratio, "{:.2%}")

        # 爬升统计
        print("\n--- 爬升统计 ---")
        safe_print("爬升成功率", team_stat.climb_success_percentage, "{:.1f}", "%")
        safe_print(
            "最短爬升时间",
            team_stat.climb_success_cycle_time_min,
            "{:.1f}",
            "s",
            show_rank=False,
        )
        safe_print("停靠时间中位数", team_stat.climb_park_time_median, "{:.1f}", "s")

        print_match_list("成功场次", team_stat.climb_success_matches)
        print_match_list("失败场次", team_stat.climb_fail_matches)
        print_match_list("碰链场次", team_stat.climb_touch_chain_matches)

        # BPS和EPA
        print("\n--- 效率指标 ---")
        safe_print("BPS值", team_stat.bps_value, "{:.3f}")
        safe_print("EPA值", team_stat.epa_value, "{:.2f}")

        # 自动阶段
        print("\n--- 自动阶段 ---")
        safe_print("越线成功率", team_stat.auto_line_cross_percentage, "{:.1f}", "%")
        safe_print(
            "高中筒成功率", team_stat.auto_high_mid_coral_success_rate, "{:.1f}", "%"
        )
        safe_print(
            "低槽筒成功率", team_stat.auto_low_slot_coral_success_rate, "{:.1f}", "%"
        )

        # 手动筒统计
        print("\n--- 手动筒统计 ---")
        safe_print("L1筒平均成功数", team_stat.l1_teleop_success_count_avg, "{:.1f}")
        safe_print("L1筒成功率", team_stat.l1_teleop_success_percentage, "{:.1f}", "%")
        safe_print("L2筒平均成功数", team_stat.l2_teleop_success_count_avg, "{:.1f}")
        safe_print("L3筒平均成功数", team_stat.l3_teleop_success_count_avg, "{:.1f}")
        safe_print("L4筒平均成功数", team_stat.l4_teleop_success_count_avg, "{:.1f}")
        safe_print(
            "槽筒平均成功数", team_stat.stack_l1_teleop_success_count_avg, "{:.1f}"
        )
        safe_print("总筒平均成功数", team_stat.total_teleop_success_count_avg, "{:.1f}")

        # 手动球统计
        print("\n--- 手动球统计 ---")
        safe_print("平均刮球数", team_stat.avg_scrape_algae_count, "{:.1f}")
        safe_print("平均捡球数", team_stat.avg_pickup_algae_count, "{:.1f}")
        safe_print(
            "球周期成功数中位数", team_stat.algae_success_cycle_count_median, "{:.1f}"
        )
        safe_print(
            "最大单场球周期",
            team_stat.algae_success_cycle_count_max,
            "{:.0f}",
            "",
            show_rank=False,
        )

        # 球来源分布
        print(
            f"球来源分布: 前场{team_stat.algae_source_front_percentage:.1%}, "
            f"中场{team_stat.algae_source_mid_percentage:.1%}, "
            f"后场{team_stat.algae_source_back_percentage:.1%}, "
            f"珊瑚{team_stat.algae_source_reef_percentage:.1%}"
        )

        # 网投统计
        safe_print("网投成功率", team_stat.net_place_success_rate, "{:.1f}", "%")
        safe_print("网射成功率", team_stat.net_shoot_success_rate, "{:.1f}", "%")

        # 防守抗性
        print("\n--- 防守抗性 ---")
        safe_print("被防守百分比", team_stat.coral_defended_percentage, "{:.1f}", "%")
        safe_print(
            "被防守最大单场",
            team_stat.coral_defended_max_single_match,
            "{:.0f}",
            "",
            show_rank=False,
        )
        safe_print(
            "被防守周期时间中位数",
            team_stat.defended_success_coral_cycle_time_median,
            "{:.1f}",
            "s",
        )
        safe_print(
            "无防守周期时间中位数",
            team_stat.undefended_success_coral_cycle_time_median,
            "{:.1f}",
            "s",
        )
        safe_print(
            "防守vs无防守时间增加",
            team_stat.defended_vs_undefended_success_coral_cycle_time_increase_percentage,
            "{:.1f}",
            "%",
        )

    print(f"\n{'='*50}")
    print("统计数据输出完成")
    print(f"{'='*50}")

    # 输出到JSON文件
    output_dir = "backend/team_statistics_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for team_stat in team_stats:
        output_file = f"{output_dir}/team_{team_stat.team_no}_statistics.json"
        try:
            team_stat.save_to_json_file(output_file)
            print(f"队伍 {team_stat.team_no} 统计数据已保存到: {output_file}")
        except Exception as e:
            print(f"保存队伍 {team_stat.team_no} 统计数据失败: {e}")

    print(f"\n所有队伍统计数据已保存到 {output_dir} 目录")
