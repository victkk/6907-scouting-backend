// 公共工具函数和功能

// 显示加载状态
function showLoading(show = true) {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

// 显示错误消息
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        const errorText = errorDiv.querySelector('.error-text');
        if (errorText) {
            errorText.textContent = message;
        } else {
            errorDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + message;
        }
        errorDiv.style.display = 'block';
        
        // 5秒后自动隐藏
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        // 如果没有错误消息框，使用alert
        alert('错误: ' + message);
    }
}

// 显示成功消息
function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        const successText = successDiv.querySelector('.success-text');
        if (successText) {
            successText.textContent = message;
        } else {
            successDiv.innerHTML = '<i class="fas fa-check-circle"></i> ' + message;
        }
        successDiv.style.display = 'block';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    } else {
        // 如果没有成功消息框，使用alert
        alert('成功: ' + message);
    }
}

// 隐藏错误消息
function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// 隐藏成功消息
function hideSuccess() {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        successDiv.style.display = 'none';
    }
}

// API 请求封装
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// 获取所有队伍
async function getTeams() {
    try {
        const response = await apiRequest('/api/teams');
        return response.data;
    } catch (error) {
        showError('获取队伍列表失败: ' + error.message);
        return [];
    }
}

// 获取所有比赛等级
async function getTournamentLevels() {
    try {
        const response = await apiRequest('/api/tournament-levels');
        return response.data;
    } catch (error) {
        showError('获取比赛等级失败: ' + error.message);
        return [];
    }
}

// 获取队伍快捷方式
async function getTeamShortcuts() {
    try {
        const response = await apiRequest('/api/team-shortcuts');
        return response.data;
    } catch (error) {
        showError('获取队伍快捷方式失败: ' + error.message);
        return {};
    }
}

// 生成队伍复选框
function generateTeamCheckboxes(teams, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    teams.forEach(team => {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-md-3';
        
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `team-${team}`;
        checkbox.value = team;
        checkbox.addEventListener('change', updateSelectedTeams);
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `team-${team}`;
        label.textContent = `队伍 ${team}`;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        colDiv.appendChild(checkDiv);
        container.appendChild(colDiv);
    });
}

// 生成比赛等级复选框
function generateTournamentLevelCheckboxes(levels, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    levels.forEach(level => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `level-${level}`;
        checkbox.value = level;
        checkbox.checked = level !== 'Practice'; // Practice比赛等级默认不勾选
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `level-${level}`;
        label.textContent = level;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        container.appendChild(checkDiv);
    });
}

// 更新已选择的队伍显示
function updateSelectedTeams() {
    const container = document.getElementById('selected-teams');
    if (!container) return;
    
    const checkboxes = document.querySelectorAll('#team-checkboxes input[type="checkbox"]:checked');
    container.innerHTML = '';
    
    checkboxes.forEach(checkbox => {
        const badge = document.createElement('span');
        badge.className = 'badge bg-primary';
        badge.textContent = `队伍 ${checkbox.value}`;
        
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'btn-close btn-close-white ms-1';
        closeBtn.style.fontSize = '0.6rem';
        closeBtn.addEventListener('click', () => {
            checkbox.checked = false;
            updateSelectedTeams();
        });
        
        badge.appendChild(closeBtn);
        container.appendChild(badge);
    });
}

// 获取选中的队伍
function getSelectedTeams() {
    const checkboxes = document.querySelectorAll('#team-checkboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// 获取选中的比赛等级
function getSelectedTournamentLevels() {
    const checkboxes = document.querySelectorAll('#tournament-level-checkboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// 解析match_no范围表达式（如1-7,9-11,15）
function parseMatchFilter(filterStr) {
    if (!filterStr || !filterStr.trim()) {
        return [];
    }
    
    const matchNos = [];
    const parts = filterStr.split(',');
    
    for (const part of parts) {
        const trimmed = part.trim();
        if (!trimmed) continue;
        
        if (trimmed.includes('-')) {
            // 处理范围，如 1-7
            const [start, end] = trimmed.split('-').map(s => parseInt(s.trim()));
            if (!isNaN(start) && !isNaN(end) && start <= end) {
                for (let i = start; i <= end; i++) {
                    matchNos.push(i);
                }
            }
        } else {
            // 处理单个数字，如 15
            const num = parseInt(trimmed);
            if (!isNaN(num)) {
                matchNos.push(num);
            }
        }
    }
    
    // 去重并排序
    return [...new Set(matchNos)].sort((a, b) => a - b);
}

// 获取match_no过滤条件
function getMatchFilter(elementId = 'match-filter') {
    const input = document.getElementById(elementId);
    if (!input) return [];
    
    return parseMatchFilter(input.value);
}

// 设置选中的队伍
function setSelectedTeams(teams) {
    // 先清除所有选中状态
    const allCheckboxes = document.querySelectorAll('#team-checkboxes input[type="checkbox"]');
    allCheckboxes.forEach(cb => cb.checked = false);
    
    // 设置指定队伍为选中
    teams.forEach(team => {
        const checkbox = document.getElementById(`team-${team}`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
    
    updateSelectedTeams();
}

// 格式化数值显示
function formatValue(value, decimals = 2) {
    if (value === null || value === undefined || value === '') {
        return '-';
    }
    
    if (typeof value === 'number') {
        return value.toFixed(decimals);
    }
    
    return value.toString();
}

// 格式化排名显示
function formatRank(rank) {
    if (rank === null || rank === undefined || rank <= 0) {
        return '-';
    }
    
    return `#${rank}`;
}

// 格式化比赛信息
function formatMatch(tournamentLevel, matchNo) {
    if (!tournamentLevel || !matchNo) {
        return '-';
    }
    
    return `${tournamentLevel}-${matchNo}`;
}

// 获取排名样式类
function getRankClass(rank) {
    if (rank === 1) return 'rank-1';
    if (rank === 2) return 'rank-2';
    if (rank === 3) return 'rank-3';
    return '';
}

// 属性显示顺序（按照team_statistics_attributes.csv中的顺序）
const ATTRIBUTE_ORDER = [
    'team_no',
    'cycle_teleop_coral_time_ratio',
    'cycle_teleop_algae_time_ratio',
    'cycle_teleop_defense_time_ratio',
    'cycle_teleop_give_up_time_ratio',
    'climb_success_matches',
    'climb_fail_matches',
    'climb_touch_chain_matches',
    'climb_success_percentage',
    'climb_success_cycle_time_min',
    'climb_park_time_median',
    'processor_success_max_single_match',
    'bps_value',
    'epa_value',
    'ppg_avg',
    'ppg_max_single_match',
    'auto_line_cross_percentage',
    'auto_preload_coral_percentage',
    'auto_high_mid_coral_max',
    'auto_high_mid_coral_success_rate',
    'auto_low_slot_coral_max',
    'auto_low_slot_coral_success_rate',
    'auto_net_place_max',
    'auto_algae_process_max',
    'coral_source_station_percentage',
    'coral_source_ground_percentage',
    'l1_teleop_success_count_avg',
    'l1_teleop_success_percentage',
    'l2_teleop_success_count_avg',
    'l2_teleop_success_percentage',
    'l3_teleop_success_count_avg',
    'l3_teleop_success_percentage',
    'l4_teleop_success_count_avg',
    'l4_teleop_success_percentage',
    'stack_l1_teleop_success_count_avg',
    'stack_l1_teleop_success_percentage',
    'l1_teleop_undefended_success_cycle_time_median',
    'l2_teleop_undefended_success_cycle_time_median',
    'l3_teleop_undefended_success_cycle_time_median',
    'l4_teleop_undefended_success_cycle_time_median',
    'stack_l1_teleop_undefended_success_cycle_time_median',
    'total_teleop_success_count_avg',
    'total_teleop_success_percentage',
    'total_teleop_undefended_success_cycle_time_median',
    'avg_scrape_algae_count',
    'avg_pickup_algae_count',
    'algae_success_cycle_count_median',
    'algae_success_cycle_count_max',
    'net_success_undefended_cycle_time_median',
    'algae_source_reef_percentage',
    'algae_source_back_percentage',
    'algae_source_mid_percentage',
    'algae_source_front_percentage',
    'net_place_percentage',
    'net_shoot_percentage',
    'net_place_success_rate',
    'net_shoot_success_rate',
    'tactical_max_single_match',
    'last_second_processer_matches',
    'coral_defended_percentage',
    'coral_defended_max_single_match',
    'defended_success_coral_cycle_time_max',
    'defended_success_coral_cycle_time_median',
    'undefended_success_coral_cycle_time_median',
    'defended_vs_undefended_success_coral_cycle_time_increase_percentage'
];

// 统计项名称的中文映射
const ATTRIBUTE_NAMES = {
    // 基本信息
    'team_no': '队伍编号',
    
    // 时间占比
    'cycle_teleop_coral_time_ratio': '筒任务时间占比',
    'cycle_teleop_algae_time_ratio': '球任务时间占比',
    'cycle_teleop_defense_time_ratio': '防守时间占比',
    'cycle_teleop_give_up_time_ratio': '放弃时间占比',
    
    // 爬升相关
    'climb_success_percentage': '爬升成功率',
    'climb_success_cycle_time_min': '最短爬升时间',
    'climb_park_time_median': '停靠时间中位数',
    'processor_success_max_single_match': '单场最大狗洞成功数',
    
    // BPS和EPA
    'bps_value': 'BPS值',
    'epa_value': 'EPA值',
    'ppg_avg': '场均得分',
    'ppg_max_single_match': '单场最高得分',
    // 自动阶段
    'auto_line_cross_percentage': '自动越线成功率',
    'auto_preload_coral_percentage': '自动预装筒成功率',
    'auto_high_mid_coral_max': '自动高中筒最大值',
    'auto_high_mid_coral_success_rate': '自动高中筒成功率',
    'auto_low_slot_coral_max': '自动低槽筒最大值',
    'auto_low_slot_coral_success_rate': '自动低槽筒成功率',
    'auto_net_place_max': '自动放网最大值',
    'auto_algae_process_max': '自动球处理最大值',
    
    // 手动筒
    'coral_source_station_percentage': '筒来源站台百分比',
    'coral_source_ground_percentage': '筒来源地面百分比',
    'l1_teleop_success_count_avg': 'L1筒平均成功数',
    'l1_teleop_success_percentage': 'L1筒成功率',
    'l2_teleop_success_count_avg': 'L2筒平均成功数',
    'l2_teleop_success_percentage': 'L2筒成功率',
    'l3_teleop_success_count_avg': 'L3筒平均成功数',
    'l3_teleop_success_percentage': 'L3筒成功率',
    'l4_teleop_success_count_avg': 'L4筒平均成功数',
    'l4_teleop_success_percentage': 'L4筒成功率',
    'stack_l1_teleop_success_count_avg': '叠筒L1平均成功数',
    'stack_l1_teleop_success_percentage': '叠筒L1成功率',
    'total_teleop_success_count_avg': '总筒平均成功数',
    'total_teleop_success_percentage': '总筒成功率',
    
    // 手动球
    'avg_scrape_algae_count': '平均刮球数',
    'avg_pickup_algae_count': '平均拾球数',
    'algae_success_cycle_count_median': '球成功周期中位数',
    'algae_success_cycle_count_max': '球成功周期最大值',
    'net_success_undefended_cycle_time_median': '无防守网成功周期中位数',
    'net_place_success_rate': '放网成功率',
    'net_shoot_success_rate': '射网成功率',
    'tactical_max_single_match': '单场最大战术值',
    
    // 防守抗性
    'coral_defended_percentage': '筒被防守百分比',
    'coral_defended_max_single_match': '单场最大被防守筒数',
    'defended_success_coral_cycle_time_max': '被防守筒成功周期最大值',
    'defended_success_coral_cycle_time_median': '被防守筒成功周期中位数',
    'undefended_success_coral_cycle_time_median': '无防守筒成功周期中位数',
    'defended_vs_undefended_success_coral_cycle_time_increase_percentage': '防守vs无防守周期时间增加百分比'
};

// 获取统计项的中文名称
function getAttributeName(attribute) {
    return ATTRIBUTE_NAMES[attribute] || attribute;
}

// 根据预定义顺序对属性进行排序
function sortAttributesByOrder(attributes) {
    return attributes.sort((a, b) => {
        const indexA = ATTRIBUTE_ORDER.indexOf(a);
        const indexB = ATTRIBUTE_ORDER.indexOf(b);
        
        // 如果两个属性都在预定义顺序中，按顺序排序
        if (indexA !== -1 && indexB !== -1) {
            return indexA - indexB;
        }
        
        // 如果只有一个在预定义顺序中，优先显示
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        
        // 如果都不在预定义顺序中，按字母顺序排序
        return a.localeCompare(b);
    });
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化提示工具
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 