// 队伍比较页面功能

// 添加悬浮表头样式 (已修复)
const style = document.createElement('style');
style.textContent = `
  .table-fixed-header thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background-color: #212529;
    color: white;
  }
`;
document.head.appendChild(style);


let teamStatistics = [];
let availableTeams = [];
let availableLevels = [];
let teamShortcuts = {};
let currentEditingShortcut = null; // 当前正在编辑的快捷组
let currentTeamOrder = null; // 当前队伍显示顺序（如有快捷方式选择）

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

// 初始化页面
async function initializePage() {
    try {
        showLoading(true);
        
        // 并行加载所有数据
        const [teams, levels, shortcuts] = await Promise.all([
            getTeams(),
            getTournamentLevels(), 
            getTeamShortcuts()
        ]);
        
        availableTeams = teams;
        availableLevels = levels;
        teamShortcuts = shortcuts;
        
        // 初始化界面
        initializeTeamShortcuts();
        initializeTeamCheckboxes();
        initializeTournamentLevelCheckboxes();
        initializeEventListeners();
        
        showLoading(false);
        
    } catch (error) {
        showError('页面初始化失败: ' + error.message);
        showLoading(false);
    }
}

// 初始化队伍快捷方式 (已更新为支持多选)
function initializeTeamShortcuts() {
    const select = document.getElementById('team-shortcuts');
    if (!select) return;
    
    select.innerHTML = ''; // 直接清空，多选框不需要提示选项
    
    Object.keys(teamShortcuts).forEach(shortcutName => {
        const option = document.createElement('option');
        option.value = shortcutName;
        option.textContent = shortcutName;
        select.appendChild(option);
    });
    
    // 更新按钮状态
    updateShortcutButtons();
}

// 更新快捷组管理按钮状态 (已更新为支持多选)
function updateShortcutButtons() {
    const select = document.getElementById('team-shortcuts');
    const editBtn = document.getElementById('edit-team-shortcut');
    const deleteBtn = document.getElementById('delete-team-shortcut');
    
    if (select && editBtn && deleteBtn) {
        // 仅当选中项数量为 1 时，才启用编辑和删除按钮
        const isSingleSelection = select.selectedOptions.length === 1;
        editBtn.disabled = !isSingleSelection;
        deleteBtn.disabled = !isSingleSelection;
    }
}

// 初始化队伍复选框
function initializeTeamCheckboxes() {
    renderTeamCheckboxes();
}

// 渲染队伍复选框
function renderTeamCheckboxes() {
    const container = document.getElementById('team-checkboxes');
    if (!container) return;
    
    container.innerHTML = '';
    
    const searchTerm = document.getElementById('team-search').value.toLowerCase();
    
    // 过滤队伍
    let baseTeams = currentTeamOrder ? [...currentTeamOrder] : [...availableTeams];
    const filteredTeams = baseTeams.filter(team =>
        team.toString().includes(searchTerm)
    );
    
    filteredTeams.forEach(team => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `team-${team}`;
        checkbox.value = team;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `team-${team}`;
        label.textContent = `队伍 ${team}`;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        container.appendChild(checkDiv);
    });
}

// 设置选中的队伍
function setSelectedTeams(teamNumbers) {
    // 清除所有选中状态
    document.querySelectorAll('#team-checkboxes input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    
    // 设置选中的队伍
    teamNumbers.forEach(teamNo => {
        const checkbox = document.getElementById(`team-${teamNo}`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
}

// 获取选中的队伍
function getSelectedTeams() {
    const checkboxes = document.querySelectorAll('#team-checkboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// 初始化比赛等级复选框
function initializeTournamentLevelCheckboxes() {
    generateTournamentLevelCheckboxes(availableLevels, 'tournament-level-checkboxes');
}

// 初始化事件监听器 (已更新为支持多选)
function initializeEventListeners() {
    // 快捷方式选择
    const shortcutSelect = document.getElementById('team-shortcuts');
    if (shortcutSelect) {
        shortcutSelect.addEventListener('change', function() {
            // 1. 获取所有被选中的快捷组名称
            const selectedShortcutNames = Array.from(this.selectedOptions).map(opt => opt.value);

            // 2. 合并所有选中快捷组的队伍，并去重
            const combinedTeams = new Set();
            selectedShortcutNames.forEach(name => {
                if (teamShortcuts[name]) {
                    teamShortcuts[name].forEach(team => combinedTeams.add(team));
                }
            });

            // 3. 将 Set 转换为排序后的数组
            const finalTeamList = Array.from(combinedTeams).sort((a, b) => a - b);
            
            if (finalTeamList.length > 0) {
                currentTeamOrder = finalTeamList;
                renderTeamCheckboxes(); 
                setSelectedTeams(finalTeamList);
            } else {
                // 如果没有选择任何快捷组
                currentTeamOrder = null; 
                // 清除所有勾选
                document.querySelectorAll('#team-checkboxes input[type="checkbox"]').forEach(cb => {
                    cb.checked = false;
                });
                renderTeamCheckboxes();
            }
            
            // 4. 更新按钮状态
            updateShortcutButtons();
        });
    }
    
    // 队伍搜索
    const searchInput = document.getElementById('team-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            renderTeamCheckboxes();
        });
    }
    
    // 刷新数据按钮
    const refreshBtn = document.getElementById('refresh-data');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
    
    // 创建快捷组按钮
    const createShortcutBtn = document.getElementById('create-shortcut');
    if (createShortcutBtn) {
        createShortcutBtn.addEventListener('click', openCreateShortcutModal);
    }
    
    // 保存快捷组按钮
    const saveShortcutBtn = document.getElementById('save-shortcut');
    if (saveShortcutBtn) {
        saveShortcutBtn.addEventListener('click', saveShortcut);
    }
    
    // 更新快捷组按钮
    const updateShortcutBtn = document.getElementById('update-shortcut');
    if (updateShortcutBtn) {
        updateShortcutBtn.addEventListener('click', updateShortcut);
    }
    
    // 编辑快捷组按钮
    const editShortcutBtn = document.getElementById('edit-team-shortcut');
    if (editShortcutBtn) {
        editShortcutBtn.addEventListener('click', editShortcut);
    }

    // 删除快捷组按钮
    const deleteShortcutBtn = document.getElementById('delete-team-shortcut');
    if (deleteShortcutBtn) {
        deleteShortcutBtn.addEventListener('click', deleteShortcut);
    }
}

// 打开创建快捷组模态框
function openCreateShortcutModal() {
    const modal = new bootstrap.Modal(document.getElementById('createShortcutModal'));
    updateShortcutItemsContainer();
    modal.show();
}

// 更新快捷组项目容器
function updateShortcutItemsContainer() {
    const container = document.getElementById('shortcut-items-container');
    
    container.innerHTML = '';
    
    // 队伍快捷组
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = '选择队伍';
    container.appendChild(label);
    
    const teamContainer = document.createElement('div');
    teamContainer.className = 'overflow-auto';
    teamContainer.style.maxHeight = '200px';
    
    // 添加样式
    teamContainer.style.padding = '10px';
    teamContainer.style.border = '1px solid #dee2e6';
    teamContainer.style.borderRadius = '0.375rem';
    
    availableTeams.forEach(team => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `shortcut-team-${team}`;
        checkbox.value = team;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `shortcut-team-${team}`;
        label.textContent = `队伍 ${team}`;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        teamContainer.appendChild(checkDiv);
    });
    
    container.appendChild(teamContainer);
}

// 保存快捷组
async function saveShortcut() {
    try {
        const name = document.getElementById('shortcut-name').value.trim();
        const type = 'team'; // 固定为队伍快捷组
        
        if (!name) {
            showError('请输入快捷组名称');
            return;
        }
        
        // 获取选中的队伍
        const checkboxes = document.querySelectorAll('#shortcut-items-container input[type="checkbox"]:checked');
        const items = Array.from(checkboxes).map(cb => parseInt(cb.value));
        
        if (items.length === 0) {
            showError('请至少选择一个队伍');
            return;
        }
        
        // 发送保存请求
        const response = await apiRequest('/api/shortcuts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                type: type,
                items: items
            })
        });
        
        if (response.success) {
            // 更新队伍快捷组
            teamShortcuts[name] = items;
            initializeTeamShortcuts();
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createShortcutModal'));
            modal.hide();
            
            // 清空表单
            document.getElementById('shortcut-form').reset();
            
            showSuccess('快捷组创建成功');
        } else {
            showError('创建快捷组失败: ' + response.message);
        }
    } catch (error) {
        showError('创建快捷组失败: ' + error.message);
    }
}

// 刷新数据
async function refreshData() {
    try {
        showLoading(true);
        hideError();
        
        const selectedTeams = getSelectedTeams();
        const selectedLevels = getSelectedTournamentLevels();
        const matchFilter = getMatchFilter('match-filter');
        
        if (selectedTeams.length === 0) {
            showError('请至少选择一个队伍');
            showLoading(false);
            return;
        }
        
        // 构建查询参数
        const params = new URLSearchParams();
        selectedTeams.forEach(team => params.append('teams', team));
        selectedLevels.forEach(level => params.append('tournament_levels', level));
        matchFilter.forEach(matchNo => params.append('match_nos', matchNo));
        
        // 获取队伍统计数据
        const response = await apiRequest('/api/team-statistics?' + params.toString());
        
        teamStatistics = response.data;
        
        // 更新比较表格
        updateComparisonTable();
        
        showLoading(false);
        
    } catch (error) {
        showError('刷新数据失败: ' + error.message);
        showLoading(false);
    }
}

// 更新比较表格
function updateComparisonTable() {
    const table = document.getElementById('comparison-table');
    const header = document.getElementById('table-header');
    const body = document.getElementById('table-body');
    
    if (!table || !header || !body) return;
    
    // 清空表格
    header.innerHTML = '<th>统计项</th>';
    body.innerHTML = '';
    
    if (teamStatistics.length === 0) {
        body.innerHTML = '<tr><td colspan="100%" class="text-center">暂无数据</td></tr>';
        return;
    }
    
    // 添加队伍列标题
    teamStatistics.forEach(teamStat => {
        const th = document.createElement('th');
        th.textContent = `队伍 ${teamStat.team_no}`;
        header.appendChild(th);
    });
    
    // 获取所有属性（除了team_no）
    const attributes = Object.keys(teamStatistics[0]).filter(key => 
        key !== 'team_no' && 
        teamStatistics.some(team => team[key] !== null && team[key] !== undefined)
    );
    
    // 根据预定义顺序对属性进行排序
    const sortedAttributes = sortAttributesByOrder(attributes);
    
    // 为每个属性创建行
    sortedAttributes.forEach(attribute => {
        const row = createComparisonRow(attribute);
        if (row) {
            body.appendChild(row);
        }
    });
}

// 创建比较行
function createComparisonRow(attribute) {
    const row = document.createElement('tr');
    
    // 统计项名称列
    const nameCell = document.createElement('td');
    nameCell.textContent = getAttributeName(attribute);
    nameCell.className = 'fw-bold';
    row.appendChild(nameCell);
    
    // 为每个队伍创建数据列
    teamStatistics.forEach(teamStat => {
        const dataCell = document.createElement('td');
        const attributeData = teamStat[attribute];
        
        if (attributeData === null || attributeData === undefined) {
            dataCell.innerHTML = '-';
        } else if (typeof attributeData === 'number') {
            // float类型：只显示值
            dataCell.innerHTML = `<span class="value-cell">${formatValue(attributeData)}</span>`;
        } else if (typeof attributeData === 'object') {
            if (attributeData.hasOwnProperty('value') && attributeData.hasOwnProperty('rank')) {
                if (attributeData.hasOwnProperty('match_no') && attributeData.hasOwnProperty('tournament_level')) {
                    // RankValueMatch类型：显示值、排名和比赛
                    dataCell.innerHTML = `
                        <div class="value-cell">${formatValue(attributeData.value)}</div>
                        <div class="rank-cell">${formatRank(attributeData.rank)}</div>
                        <div class="match-cell">${formatMatch(attributeData.tournament_level, attributeData.match_no)}</div>
                    `;
                } else {
                    // RankValue类型：显示值和排名
                    dataCell.innerHTML = `
                        <div class="value-cell">${formatValue(attributeData.value)}</div>
                        <div class="rank-cell">${formatRank(attributeData.rank)}</div>
                    `;
                }
                
                // 添加排名样式
                const rankClass = getRankClass(attributeData.rank);
                if (rankClass) {
                    dataCell.classList.add(rankClass);
                }
            } else if (attributeData.hasOwnProperty('match_nos') && attributeData.hasOwnProperty('tournament_levels')) {
                // MatchList类型：显示比赛组合
                const matches = [];
                for (let i = 0; i < Math.min(attributeData.match_nos.length, attributeData.tournament_levels.length); i++) {
                    matches.push(formatMatch(attributeData.tournament_levels[i], attributeData.match_nos[i]));
                }
                dataCell.innerHTML = matches.length > 0 ? matches.join(', ') : '-';
            } else {
                dataCell.innerHTML = '-';
            }
        } else {
            dataCell.innerHTML = attributeData.toString();
        }
        
        row.appendChild(dataCell);
    });
    
    return row;
}

// 导出数据功能
function exportData() {
    if (teamStatistics.length === 0) {
        showError('没有可导出的数据');
        return;
    }
    
    try {
        const csvContent = generateCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `team_comparison_${new Date().toISOString().slice(0, 10)}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    } catch (error) {
        showError('导出数据失败: ' + error.message);
    }
}

// 生成CSV内容
function generateCSV() {
    if (teamStatistics.length === 0) return '';
    
    const lines = [];
    
    // 标题行
    const headers = ['统计项'];
    teamStatistics.forEach(teamStat => {
        headers.push(`队伍 ${teamStat.team_no}`);
    });
    lines.push(headers.join(','));
    
    // 数据行
    const attributes = Object.keys(teamStatistics[0]).filter(key => key !== 'team_no');
    const sortedAttributes = sortAttributesByOrder(attributes);
    
    sortedAttributes.forEach(attribute => {
        const row = [getAttributeName(attribute)];
        
        teamStatistics.forEach(teamStat => {
            const attributeData = teamStat[attribute];
            let cellValue = '';
            
            if (attributeData === null || attributeData === undefined) {
                cellValue = '-';
            } else if (typeof attributeData === 'number') {
                cellValue = formatValue(attributeData);
            } else if (typeof attributeData === 'object') {
                if (attributeData.hasOwnProperty('value')) {
                    cellValue = `${formatValue(attributeData.value)} (${formatRank(attributeData.rank)})`;
                    if (attributeData.hasOwnProperty('match_no')) {
                        cellValue += ` ${formatMatch(attributeData.tournament_level, attributeData.match_no)}`;
                    }
                } else if (attributeData.hasOwnProperty('match_nos')) {
                    const matches = [];
                    for (let i = 0; i < Math.min(attributeData.match_nos.length, attributeData.tournament_levels.length); i++) {
                        matches.push(formatMatch(attributeData.tournament_levels[i], attributeData.match_nos[i]));
                    }
                    cellValue = matches.join('; ');
                }
            } else {
                cellValue = attributeData.toString();
            }
            
            row.push(cellValue);
        });
        
        lines.push(row.join(','));
    });
    
    return lines.join('\n');
}

// 添加导出按钮到页面
document.addEventListener('DOMContentLoaded', function() {
    const refreshBtn = document.getElementById('refresh-data');
    if (refreshBtn) {
        const exportBtn = document.createElement('button');
        exportBtn.type = 'button';
        exportBtn.className = 'btn btn-success ms-2';
        exportBtn.innerHTML = '<i class="fas fa-download"></i> 导出数据';
        exportBtn.addEventListener('click', exportData);
        
        refreshBtn.parentNode.appendChild(exportBtn);
    }
}); 

// 编辑快捷组
function editShortcut() {
    const select = document.getElementById('team-shortcuts');
    // 从 selectedOptions 获取值，因为现在是多选
    const selectedShortcut = select.selectedOptions.length === 1 ? select.selectedOptions[0].value : null;
    
    if (!selectedShortcut || !teamShortcuts[selectedShortcut]) {
        showError('请先只选择一个要编辑的快捷组');
        return;
    }
    
    currentEditingShortcut = {
        oldName: selectedShortcut,
        type: 'team'
    };
    
    // 设置编辑表单的值
    document.getElementById('edit-shortcut-name').value = selectedShortcut;
    document.getElementById('edit-shortcut-type-team').checked = true;
    
    // 更新编辑表单的项目容器
    updateEditShortcutItemsContainer();
    
    // 设置当前快捷组的选中项
    const currentItems = teamShortcuts[selectedShortcut];
    setTimeout(() => {
        currentItems.forEach(item => {
            const checkbox = document.getElementById(`edit-shortcut-team-${item}`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    }, 100);
    
    const modal = new bootstrap.Modal(document.getElementById('editShortcutModal'));
    modal.show();
}

// 删除快捷组
async function deleteShortcut() {
    const select = document.getElementById('team-shortcuts');
    const selectedShortcut = select.selectedOptions.length === 1 ? select.selectedOptions[0].value : null;

    if (!selectedShortcut) {
        showError('请先只选择一个要删除的快捷组');
        return;
    }
    
    if (!confirm(`确定要删除快捷组"${selectedShortcut}"吗？此操作不可撤销。`)) {
        return;
    }
    
    try {
        const response = await apiRequest(`/api/shortcuts/${encodeURIComponent(selectedShortcut)}/team`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            // 从本地数据中删除
            delete teamShortcuts[selectedShortcut];
            
            // 重新初始化快捷组选择
            initializeTeamShortcuts();
            
            showSuccess('快捷组删除成功');
        } else {
            showError('删除快捷组失败: ' + response.message);
        }
    } catch (error) {
        showError('删除快捷组失败: ' + error.message);
    }
}

// 更新编辑表单的项目容器
function updateEditShortcutItemsContainer() {
    const container = document.getElementById('edit-shortcut-items-container');
    
    container.innerHTML = '';
    
    // 队伍快捷组
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = '选择队伍';
    container.appendChild(label);
    
    const teamContainer = document.createElement('div');
    teamContainer.className = 'overflow-auto';
    teamContainer.style.maxHeight = '200px';
    
    // 添加样式
    teamContainer.style.padding = '10px';
    teamContainer.style.border = '1px solid #dee2e6';
    teamContainer.style.borderRadius = '0.375rem';
    
    availableTeams.forEach(team => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `edit-shortcut-team-${team}`;
        checkbox.value = team;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `edit-shortcut-team-${team}`;
        label.textContent = `队伍 ${team}`;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        teamContainer.appendChild(checkDiv);
    });
    
    container.appendChild(teamContainer);
}

// 更新快捷组
async function updateShortcut() {
    try {
        if (!currentEditingShortcut) {
            showError('没有正在编辑的快捷组');
            return;
        }
        
        const name = document.getElementById('edit-shortcut-name').value.trim();
        
        if (!name) {
            showError('请输入快捷组名称');
            return;
        }
        
        const checkboxes = document.querySelectorAll('#edit-shortcut-items-container input[type="checkbox"]:checked');
        const items = Array.from(checkboxes).map(cb => parseInt(cb.value));
        
        if (items.length === 0) {
            showError('请至少选择一个队伍');
            return;
        }
        
        // 发送更新请求
        const response = await apiRequest(`/api/shortcuts/${encodeURIComponent(currentEditingShortcut.oldName)}/${currentEditingShortcut.type}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                items: items
            })
        });
        
        if (response.success) {
            // 更新本地快捷组数据
            if (currentEditingShortcut.oldName !== name) {
                delete teamShortcuts[currentEditingShortcut.oldName];
            }
            teamShortcuts[name] = items;
            
            // 重新初始化快捷组选择
            initializeTeamShortcuts();
            
            // 选中刚更新的快捷组
            // In multi-select mode, we can't just set .value. We find the option and set its .selected property.
            const select = document.getElementById('team-shortcuts');
            Array.from(select.options).forEach(opt => {
                opt.selected = opt.value === name;
            });
            select.dispatchEvent(new Event('change')); // Manually trigger change to update everything
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('editShortcutModal'));
            modal.hide();
            
            // 清空编辑状态
            currentEditingShortcut = null;
            
            showSuccess('快捷组修改成功');
        } else {
            showError('修改快捷组失败: ' + response.message);
        }
    } catch (error) {
        showError('修改快捷组失败: ' + error.message);
    }
}