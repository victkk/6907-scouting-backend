// 排名展示页面功能

let rankingData = [];
let availableLevels = [];
let rankingAttributes = [];
let attributeShortcuts = {};
let currentEditingShortcut = null; // 当前正在编辑的快捷组

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

// 初始化页面
async function initializePage() {
    try {
        showLoading(true);
        
        // 加载比赛等级数据和属性快捷方式
        const [levels, shortcuts] = await Promise.all([
            getTournamentLevels(),
            getAttributeShortcuts()
        ]);
        
        availableLevels = levels;
        attributeShortcuts = shortcuts;
        
        // 初始化界面
        await initializeRankingAttributes();
        initializeAttributeShortcuts();
        initializeTournamentLevelCheckboxes();
        initializeEventListeners();
        
        showLoading(false);
        
    } catch (error) {
        showError('页面初始化失败: ' + error.message);
        showLoading(false);
    }
}

// 获取属性快捷方式
async function getAttributeShortcuts() {
    try {
        const response = await apiRequest('/api/attribute-shortcuts');
        return response.data;
    } catch (error) {
        console.warn('获取属性快捷方式失败:', error);
        return {};
    }
}

// 初始化属性快捷方式
function initializeAttributeShortcuts() {
    const select = document.getElementById('attribute-shortcuts');
    const editBtn = document.getElementById('edit-attribute-shortcut');
    const deleteBtn = document.getElementById('delete-attribute-shortcut');
    
    if (!select) return;
    
    select.innerHTML = '<option value="">选择属性快捷方式...</option>';
    
    Object.keys(attributeShortcuts).forEach(shortcutName => {
        const option = document.createElement('option');
        option.value = shortcutName;
        option.textContent = shortcutName;
        select.appendChild(option);
    });
    
    // 更新按钮状态
    updateShortcutButtons();
}

// 更新快捷组管理按钮状态
function updateShortcutButtons() {
    const select = document.getElementById('attribute-shortcuts');
    const editBtn = document.getElementById('edit-attribute-shortcut');
    const deleteBtn = document.getElementById('delete-attribute-shortcut');
    
    if (select && editBtn && deleteBtn) {
        const hasSelection = select.value !== '';
        editBtn.disabled = !hasSelection;
        deleteBtn.disabled = !hasSelection;
    }
}

// 获取所有可排名属性
async function getAllRankingAttributes() {
    try {
        const response = await apiRequest('/api/all-team-attributes');
        return response.data.filter(attr => 
            // 排除team_no，只包含可以用于排名的属性
            attr !== 'team_no'
        ).map(attr => {
            // 判断属性类型：带_max、_min后缀的通常是RankValueMatch类型
            const type = (attr.includes('_max') || attr.includes('_min')) ? 'RankValueMatch' : 'RankValue';
            return {
                key: attr,
                name: getAttributeName(attr), // 使用common.js的getAttributeName函数
                type: type
            };
        });
    } catch (error) {
        console.warn('获取排名属性失败:', error);
        return [];
    }
}

// 初始化排名属性选择
async function initializeRankingAttributes() {
    const container = document.getElementById('ranking-attributes-checkboxes');
    if (!container) return;
    
    // 从API获取属性列表
    rankingAttributes = await getAllRankingAttributes();
    
    renderRankingAttributes();
}

// 渲染排名属性
function renderRankingAttributes() {
    const container = document.getElementById('ranking-attributes-checkboxes');
    if (!container) return;
    
    container.innerHTML = '';
    
    const searchTerm = document.getElementById('attribute-search').value.toLowerCase();
    
    // 过滤属性
    const filteredAttributes = rankingAttributes.filter(attr =>
        attr.name.toLowerCase().includes(searchTerm) ||
        attr.key.toLowerCase().includes(searchTerm)
    );
    
    filteredAttributes.forEach(attr => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `attr-${attr.key}`;
        checkbox.value = attr.key;
        checkbox.dataset.type = attr.type;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `attr-${attr.key}`;
        label.textContent = attr.name;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        container.appendChild(checkDiv);
    });
}

// 设置选中的属性
function setSelectedAttributes(attributeKeys) {
    // 清除所有选中状态
    document.querySelectorAll('#ranking-attributes-checkboxes input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    
    // 设置选中的属性
    attributeKeys.forEach(key => {
        const checkbox = document.getElementById(`attr-${key}`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
}

// 初始化比赛等级复选框
function initializeTournamentLevelCheckboxes() {
    generateTournamentLevelCheckboxes(availableLevels, 'tournament-level-checkboxes');
}

// 获取选中的排名属性
function getSelectedRankingAttributes() {
    const checkboxes = document.querySelectorAll('#ranking-attributes-checkboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => ({
        key: cb.value,
        type: cb.dataset.type,
        name: cb.nextElementSibling.textContent
    }));
}

// 初始化事件监听器
function initializeEventListeners() {
    // 属性快捷方式选择
    const shortcutSelect = document.getElementById('attribute-shortcuts');
    if (shortcutSelect) {
        shortcutSelect.addEventListener('change', function() {
            if (this.value && attributeShortcuts[this.value]) {
                setSelectedAttributes(attributeShortcuts[this.value]);
            }
            updateShortcutButtons();
        });
    }
    
    // 属性搜索
    const searchInput = document.getElementById('attribute-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            renderRankingAttributes();
        });
    }
    
    // 刷新排名按钮
    const refreshBtn = document.getElementById('refresh-ranking');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshRanking);
    }
    
    // 创建快捷组按钮
    const createShortcutBtn = document.getElementById('create-shortcut');
    if (createShortcutBtn) {
        createShortcutBtn.addEventListener('click', openCreateShortcutModal);
    }
    
    // 编辑快捷组按钮
    const editShortcutBtn = document.getElementById('edit-attribute-shortcut');
    if (editShortcutBtn) {
        editShortcutBtn.addEventListener('click', openEditShortcutModal);
    }
    
    // 删除快捷组按钮
    const deleteShortcutBtn = document.getElementById('delete-attribute-shortcut');
    if (deleteShortcutBtn) {
        deleteShortcutBtn.addEventListener('click', deleteShortcut);
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
    
    // 属性快捷组
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = '选择属性';
    container.appendChild(label);
    
    const attributeContainer = document.createElement('div');
    attributeContainer.className = 'overflow-auto';
    attributeContainer.style.maxHeight = '200px';
    
    rankingAttributes.forEach(attr => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `shortcut-attr-${attr.key}`;
        checkbox.value = attr.key;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `shortcut-attr-${attr.key}`;
        label.textContent = attr.name;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        attributeContainer.appendChild(checkDiv);
    });
    
    container.appendChild(attributeContainer);
}

// 保存快捷组
async function saveShortcut() {
    try {
        const name = document.getElementById('shortcut-name').value.trim();
        const type = 'attribute'; // 固定为属性快捷组
        
        if (!name) {
            showError('请输入快捷组名称');
            return;
        }
        
        // 获取选中的属性
        const checkboxes = document.querySelectorAll('#shortcut-items-container input[type="checkbox"]:checked');
        const items = Array.from(checkboxes).map(cb => cb.value);
        
        if (items.length === 0) {
            showError('请至少选择一个属性');
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
            // 更新属性快捷组
            attributeShortcuts[name] = items;
            initializeAttributeShortcuts();
            
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

// 打开编辑快捷组模态框
function openEditShortcutModal() {
    const select = document.getElementById('attribute-shortcuts');
    const selectedShortcut = select.value;
    
    if (!selectedShortcut || !attributeShortcuts[selectedShortcut]) {
        showError('请先选择要编辑的快捷组');
        return;
    }
    
    currentEditingShortcut = {
        oldName: selectedShortcut,
        type: 'attribute'
    };
    
    // 设置编辑表单的值
    document.getElementById('edit-shortcut-name').value = selectedShortcut;
    document.getElementById('edit-shortcut-type-attribute').checked = true;
    
    // 更新编辑表单的项目容器
    updateEditShortcutItemsContainer();
    
    // 设置当前快捷组的选中项
    const currentItems = attributeShortcuts[selectedShortcut];
    setTimeout(() => {
        currentItems.forEach(item => {
            const checkbox = document.getElementById(`edit-shortcut-attr-${item}`);
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
    const select = document.getElementById('attribute-shortcuts');
    const selectedShortcut = select.value;
    
    if (!selectedShortcut) {
        showError('请先选择要删除的快捷组');
        return;
    }
    
    if (!confirm(`确定要删除快捷组"${selectedShortcut}"吗？此操作不可撤销。`)) {
        return;
    }
    
    try {
        const response = await apiRequest(`/api/shortcuts/${encodeURIComponent(selectedShortcut)}/attribute`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            // 从本地数据中删除
            delete attributeShortcuts[selectedShortcut];
            
            // 重新初始化快捷组选择
            initializeAttributeShortcuts();
            
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
    
    // 属性快捷组
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = '选择属性';
    container.appendChild(label);
    
    const attributeContainer = document.createElement('div');
    attributeContainer.className = 'overflow-auto';
    attributeContainer.style.maxHeight = '200px';
    
    rankingAttributes.forEach(attr => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `edit-shortcut-attr-${attr.key}`;
        checkbox.value = attr.key;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `edit-shortcut-attr-${attr.key}`;
        label.textContent = attr.name;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        attributeContainer.appendChild(checkDiv);
    });
    
    container.appendChild(attributeContainer);
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
        const items = Array.from(checkboxes).map(cb => cb.value);
        
        if (items.length === 0) {
            showError('请至少选择一个属性');
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
                delete attributeShortcuts[currentEditingShortcut.oldName];
            }
            attributeShortcuts[name] = items;
            
            // 重新初始化快捷组选择
            initializeAttributeShortcuts();
            
            // 选中刚更新的快捷组
            document.getElementById('attribute-shortcuts').value = name;
            updateShortcutButtons();
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('editShortcutModal'));
            modal.hide();
            setSelectedAttributes(attributeShortcuts[name]);
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

// 刷新排名
async function refreshRanking() {
    try {
        showLoading(true);
        hideError();
        
        const selectedAttributes = getSelectedRankingAttributes();
        const selectedLevels = getSelectedTournamentLevels();
        const matchFilter = getMatchFilter('match-filter-ranking');
        
        if (selectedAttributes.length === 0) {
            showError('请至少选择一个排名属性');
            showLoading(false);
            return;
        }
        
        // 获取所有选中属性的排名数据
        const allRankingData = {};
        
        for (const attr of selectedAttributes) {
            // 构建查询参数
            const params = new URLSearchParams();
            params.append('attribute', attr.key);
            selectedLevels.forEach(level => params.append('tournament_levels', level));
            matchFilter.forEach(matchNo => params.append('match_nos', matchNo));
            
            const response = await apiRequest('/api/rankings?' + params.toString());
            allRankingData[attr.key] = {
                data: response.data,
                name: attr.name,
                type: attr.type
            };
        }
        
        rankingData = allRankingData;
        
        // 更新排名表格
        updateRankingTable();
        
        showLoading(false);
        
    } catch (error) {
        showError('刷新排名失败: ' + error.message);
        showLoading(false);
    }
}

// 更新排名表格
function updateRankingTable() {
    const header = document.getElementById('ranking-header');
    const body = document.getElementById('ranking-body');
    
    if (!header || !body) return;
    
    // 清空表格
    header.innerHTML = '';
    body.innerHTML = '';
    
    if (Object.keys(rankingData).length === 0) {
        body.innerHTML = '<tr><td colspan="100%" class="text-center">暂无数据</td></tr>';
        return;
    }

    // 确定要显示的排名数量（所有属性中最大的排名数量）
    let maxRankCount = 0;
    Object.values(rankingData).forEach(attrData => {
        if (attrData.data.length > maxRankCount) {
            maxRankCount = attrData.data.length;
        }
    });

    // 生成表头 - 分两行
    const headerRow1 = document.createElement('tr');
    const headerRow2 = document.createElement('tr');
    
    // 排名列
    const rankHeader1 = document.createElement('th');
    rankHeader1.textContent = 'ranking';
    rankHeader1.rowSpan = 2;
    rankHeader1.className = 'text-center';
    headerRow1.appendChild(rankHeader1);
    
    // 为每个属性创建两列（数值列和队伍列）
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        
        // 第一行：属性名跨越两列
        const attrHeader1 = document.createElement('th');
        attrHeader1.textContent = attrData.name;
        attrHeader1.className = 'text-center';
        attrHeader1.colSpan = 2;
        headerRow1.appendChild(attrHeader1);
        
        // 第二行：数值列
        const valueHeader2 = document.createElement('th');
        valueHeader2.textContent = attrData.name;
        valueHeader2.className = 'text-center';
        headerRow2.appendChild(valueHeader2);
        
        // 第二行：队伍列
        const teamHeader2 = document.createElement('th');
        teamHeader2.textContent = 'team';
        teamHeader2.className = 'text-center';
        headerRow2.appendChild(teamHeader2);
    });
    
    header.appendChild(headerRow1);
    header.appendChild(headerRow2);
    
    // 生成数据行
    for (let rank = 1; rank <= maxRankCount; rank++) {
        const row = document.createElement('tr');
        
        // 排名列
        const rankCell = document.createElement('td');
        rankCell.className = 'text-center fw-bold';
        rankCell.textContent = rank;
        
        // 添加排名样式
        const rankClass = getRankClass(rank);
        if (rankClass) {
            rankCell.classList.add(rankClass);
        }
        
        row.appendChild(rankCell);
        
        // 为每个属性添加数值列和队伍列
        Object.keys(rankingData).forEach(attrKey => {
            const attrData = rankingData[attrKey];
            
            // 找到该排名的数据
            const rankedData = attrData.data.find(item => item.rank === rank);
            
            // 数值列
            const valueCell = document.createElement('td');
            valueCell.className = 'text-center';
            
            // 队伍列
            const teamCell = document.createElement('td');
            teamCell.className = 'text-center';
            
            if (rankedData) {
                // 数值列显示数值
                valueCell.textContent = formatValue(rankedData.value);
                
                // 队伍列显示队伍号
                teamCell.textContent = rankedData.team_no;
                
                // 添加排名样式
                if (rankClass) {
                    valueCell.classList.add(rankClass);
                    teamCell.classList.add(rankClass);
                }
            } else {
                valueCell.textContent = '-';
                teamCell.textContent = '-';
            }
            
            row.appendChild(valueCell);
            row.appendChild(teamCell);
        });
        
        body.appendChild(row);
    }
}

// 导出排名数据
function exportRankingData() {
    if (Object.keys(rankingData).length === 0) {
        showError('没有可导出的排名数据');
        return;
    }
    
    try {
        const csvContent = generateRankingCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            
            const selectedAttributes = getSelectedRankingAttributes();
            const attributeNames = selectedAttributes.map(attr => attr.name).join('_');
            link.setAttribute('download', `排名展示_${attributeNames}_${new Date().toISOString().slice(0, 10)}.csv`);
            
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    } catch (error) {
        showError('导出排名数据失败: ' + error.message);
    }
}

// 生成排名CSV内容
function generateRankingCSV() {
    if (Object.keys(rankingData).length === 0) return '';
    
    const lines = [];
    
    // 确定要显示的排名数量
    let maxRankCount = 0;
    Object.values(rankingData).forEach(attrData => {
        if (attrData.data.length > maxRankCount) {
            maxRankCount = attrData.data.length;
        }
    });
    
    // 第一行标题
    const headers1 = ['ranking'];
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        headers1.push(attrData.name);
        headers1.push(''); // 空白列，因为第一行属性名跨越两列
    });
    lines.push(headers1.join(','));
    
    // 第二行标题
    const headers2 = ['ranking'];
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        headers2.push(attrData.name); // 数值列
        headers2.push('team'); // 队伍列
    });
    lines.push(headers2.join(','));
    
    // 数据行
    for (let rank = 1; rank <= maxRankCount; rank++) {
        const row = [rank];
        
        Object.keys(rankingData).forEach(attrKey => {
            const attrData = rankingData[attrKey];
            const rankedData = attrData.data.find(item => item.rank === rank);
            
            if (rankedData) {
                const value = formatValue(rankedData.value);
                const team = rankedData.team_no;
                row.push(value); // 数值列
                row.push(team); // 队伍列
            } else {
                row.push('-'); // 数值列
                row.push('-'); // 队伍列
            }
        });
        
        lines.push(row.join(','));
    }
    
    return lines.join('\n');
}

// 添加导出按钮到页面
document.addEventListener('DOMContentLoaded', function() {
    const refreshBtn = document.getElementById('refresh-ranking');
    if (refreshBtn) {
        const exportBtn = document.createElement('button');
        exportBtn.type = 'button';
        exportBtn.className = 'btn btn-success ms-2';
        exportBtn.innerHTML = '<i class="fas fa-download"></i> 导出排名';
        exportBtn.addEventListener('click', exportRankingData);
        
        refreshBtn.parentNode.appendChild(exportBtn);
    }
}); 