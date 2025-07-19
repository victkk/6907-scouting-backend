// 排名展示页面功能

let rankingData = [];
let availableLevels = [];
let rankingAttributes = [];
let selectedAttributeKeys = new Set(); // --- [新增] 使用 Set 来存储所有已勾选属性的 key
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
            attr !== 'team_no'
        ).map(attr => {
            const type = (attr.includes('_max') || attr.includes('_min')) ? 'RankValueMatch' : 'RankValue';
            return {
                key: attr,
                name: getAttributeName(attr),
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
    
    rankingAttributes = await getAllRankingAttributes();
    
    renderRankingAttributes();
}

// --- [函数已修改] 渲染排名属性
function renderRankingAttributes() {
    const container = document.getElementById('ranking-attributes-checkboxes');
    if (!container) return;
    
    container.innerHTML = ''; // 依然先清空
    
    const searchTerm = document.getElementById('attribute-search').value.toLowerCase();
    
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
        console.log("fuck");
        // 关键改动1: 根据 selectedAttributeKeys 集合来决定是否勾选
        checkbox.checked = selectedAttributeKeys.has(attr.key);
        
        // 关键改动2: 添加事件监听，实时更新 selectedAttributeKeys
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                selectedAttributeKeys.add(attr.key);
                
            } else {
                selectedAttributeKeys.delete(attr.key);
                console.log("fuck");
            }
        });
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `attr-${attr.key}`;
        label.textContent = attr.name;
        
        checkDiv.appendChild(checkbox);
        checkDiv.appendChild(label);
        container.appendChild(checkDiv);
    });
}

// --- [函数已修改] 设置选中的属性
function setSelectedAttributes(attributeKeys) {
    // 关键改动: 直接更新数据状态，而不是操作DOM
    selectedAttributeKeys = new Set(attributeKeys);
    
    // 调用渲染函数，让界面根据最新的数据状态来更新
    renderRankingAttributes();
}

// 初始化比赛等级复选框
function initializeTournamentLevelCheckboxes() {
    generateTournamentLevelCheckboxes(availableLevels, 'tournament-level-checkboxes');
}

// --- [函数已修改] 获取选中的排名属性
function getSelectedRankingAttributes() {
    // 关键改动: 从 selectedAttributeKeys 中获取数据，而不是从DOM中查找
    return Array.from(selectedAttributeKeys).map(key => {
        // 从完整的属性列表中找到对应的属性对象
        const attribute = rankingAttributes.find(attr => attr.key === key);
        // 如果找不到，提供一个回退对象，以增强代码健壮性
        return attribute || { key: key, name: 'Unknown Attribute', type: 'Unknown' };
    });
}

// 初始化事件监听器
function initializeEventListeners() {
    // 属性快捷方式选择
    const shortcutSelect = document.getElementById('attribute-shortcuts');
    if (shortcutSelect) {
        shortcutSelect.addEventListener('change', function() {
            const selectedShortcutName = this.value;
            if (selectedShortcutName && attributeShortcuts[selectedShortcutName]) {
                // 当选择快捷组时，调用已修改的 setSelectedAttributes
                setSelectedAttributes(attributeShortcuts[selectedShortcutName]);
            } else if (!selectedShortcutName) {
                // 如果取消选择快捷组，清空所有勾选
                setSelectedAttributes([]);
            }
            updateShortcutButtons();
        });
    }
    
    // 属性搜索
    const searchInput = document.getElementById('attribute-search');
    if (searchInput) {
        searchInput.addEventListener('input', renderRankingAttributes);
    }
    
    // 刷新排名按钮
    const refreshBtn = document.getElementById('refresh-ranking');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshRanking);
    }
    
    // (后面的事件监听器代码保持不变)
    const createShortcutBtn = document.getElementById('create-shortcut');
    if (createShortcutBtn) {
        createShortcutBtn.addEventListener('click', openCreateShortcutModal);
    }
    
    const editShortcutBtn = document.getElementById('edit-attribute-shortcut');
    if (editShortcutBtn) {
        editShortcutBtn.addEventListener('click', openEditShortcutModal);
    }
    
    const deleteShortcutBtn = document.getElementById('delete-attribute-shortcut');
    if (deleteShortcutBtn) {
        deleteShortcutBtn.addEventListener('click', deleteShortcut);
    }
    
    const saveShortcutBtn = document.getElementById('save-shortcut');
    if (saveShortcutBtn) {
        saveShortcutBtn.addEventListener('click', saveShortcut);
    }
    
    const updateShortcutBtn = document.getElementById('update-shortcut');
    if (updateShortcutBtn) {
        updateShortcutBtn.addEventListener('click', updateShortcut);
    }
}

// (从此处开始到文件末尾的其他函数，都不需要做任何修改，因为它们的功能不直接依赖于主页面的复选框状态，或者通过调用已修改的函数来间接实现功能)

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
        const type = 'attribute'; 
        
        if (!name) {
            showError('请输入快捷组名称');
            return;
        }
        
        const checkboxes = document.querySelectorAll('#shortcut-items-container input[type="checkbox"]:checked');
        const items = Array.from(checkboxes).map(cb => cb.value);
        
        if (items.length === 0) {
            showError('请至少选择一个属性');
            return;
        }
        
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
            attributeShortcuts[name] = items;
            initializeAttributeShortcuts();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('createShortcutModal'));
            modal.hide();
            
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
    
    document.getElementById('edit-shortcut-name').value = selectedShortcut;
    document.getElementById('edit-shortcut-type-attribute').checked = true;
    
    updateEditShortcutItemsContainer();
    
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
            delete attributeShortcuts[selectedShortcut];
            
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
            if (currentEditingShortcut.oldName !== name) {
                delete attributeShortcuts[currentEditingShortcut.oldName];
            }
            attributeShortcuts[name] = items;
            
            initializeAttributeShortcuts();
            
            document.getElementById('attribute-shortcuts').value = name;
            updateShortcutButtons();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('editShortcutModal'));
            modal.hide();
            setSelectedAttributes(attributeShortcuts[name]); // 确保主页面也更新
            
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
        
        const allRankingData = {};
        
        for (const attr of selectedAttributes) {
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
    
    header.innerHTML = '';
    body.innerHTML = '';
    
    if (Object.keys(rankingData).length === 0) {
        body.innerHTML = '<tr><td colspan="100%" class="text-center">暂无数据</td></tr>';
        return;
    }

    // 为每个属性创建排序后的数据
    const sortedData = {};
    const equalValueMap = {}; // 记录每个属性中相同值的队伍
    
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        // 按排名排序，相同排名按队伍号排序
        sortedData[attrKey] = attrData.data.sort((a, b) => {
            if (a.rank !== b.rank) {
                return a.rank - b.rank;
            }
            return a.team_no - b.team_no;
        });
        
        // 检测相同值的队伍
        equalValueMap[attrKey] = new Set();
        for (let i = 0; i < sortedData[attrKey].length; i++) {
            for (let j = i + 1; j < sortedData[attrKey].length; j++) {
                if (sortedData[attrKey][i].value === sortedData[attrKey][j].value) {
                    equalValueMap[attrKey].add(i);
                    equalValueMap[attrKey].add(j);
                }
            }
        }
    });

    // 计算最大行数（所有属性中最大的数据量）
    let maxRowCount = 0;
    Object.values(sortedData).forEach(data => {
        if (data.length > maxRowCount) {
            maxRowCount = data.length;
        }
    });

    const headerRow1 = document.createElement('tr');
    const headerRow2 = document.createElement('tr');
    
    const rankHeader1 = document.createElement('th');
    rankHeader1.textContent = 'ranking';
    rankHeader1.rowSpan = 2;
    rankHeader1.className = 'text-center';
    headerRow1.appendChild(rankHeader1);
    
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        
        const attrHeader1 = document.createElement('th');
        attrHeader1.textContent = attrData.name;
        attrHeader1.className = 'text-center';
        attrHeader1.colSpan = 2;
        headerRow1.appendChild(attrHeader1);
        
        const valueHeader2 = document.createElement('th');
        valueHeader2.textContent = attrData.name;
        valueHeader2.className = 'text-center';
        headerRow2.appendChild(valueHeader2);
        
        const teamHeader2 = document.createElement('th');
        teamHeader2.textContent = 'team';
        teamHeader2.className = 'text-center';
        headerRow2.appendChild(teamHeader2);
    });
    
    header.appendChild(headerRow1);
    header.appendChild(headerRow2);
    
    // 为每一行创建数据
    for (let rowIndex = 0; rowIndex < maxRowCount; rowIndex++) {
        const row = document.createElement('tr');
        
        // 最左侧的rank列按照1、2、3、4的顺序显示
        const rankCell = document.createElement('td');
        rankCell.className = 'text-center fw-bold';
        rankCell.textContent = rowIndex + 1;
        
        const rankClass = getRankClass(rowIndex + 1);
        if (rankClass) {
            rankCell.classList.add(rankClass);
        }
        
        row.appendChild(rankCell);
        
        Object.keys(sortedData).forEach(attrKey => {
            const attrData = sortedData[attrKey];
            const rankedData = attrData[rowIndex];
            
            const valueCell = document.createElement('td');
            valueCell.className = 'text-center position-relative';
            
            const teamCell = document.createElement('td');
            teamCell.className = 'text-center position-relative';
            
            if (rankedData) {
                valueCell.textContent = formatValue(rankedData.value);
                teamCell.textContent = rankedData.team_no;
                
                // 检查是否有相同值，如果有则添加等号标记
                if (equalValueMap[attrKey] && equalValueMap[attrKey].has(rowIndex)) {
                    const equalMark = document.createElement('span');
                    equalMark.textContent = '=';
                    equalMark.className = 'position-absolute top-0 end-0 badge bg-secondary';
                    equalMark.style.fontSize = '0.6rem';
                    equalMark.style.transform = 'translate(25%, -25%)';
                    
                    valueCell.appendChild(equalMark);
                    teamCell.appendChild(equalMark.cloneNode(true));
                }
                
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
    
    // 为每个属性创建排序后的数据（与表格显示逻辑保持一致）
    const sortedData = {};
    const equalValueMap = {}; // 记录每个属性中相同值的队伍
    
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        // 按排名排序，相同排名按队伍号排序
        sortedData[attrKey] = attrData.data.sort((a, b) => {
            if (a.rank !== b.rank) {
                return a.rank - b.rank;
            }
            return a.team_no - b.team_no;
        });
        
        // 检测相同值的队伍
        equalValueMap[attrKey] = new Set();
        for (let i = 0; i < sortedData[attrKey].length; i++) {
            for (let j = i + 1; j < sortedData[attrKey].length; j++) {
                if (sortedData[attrKey][i].value === sortedData[attrKey][j].value) {
                    equalValueMap[attrKey].add(i);
                    equalValueMap[attrKey].add(j);
                }
            }
        }
    });
    
    // 计算最大行数
    let maxRowCount = 0;
    Object.values(sortedData).forEach(data => {
        if (data.length > maxRowCount) {
            maxRowCount = data.length;
        }
    });
    
    const headers1 = ['ranking'];
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        headers1.push(attrData.name);
        headers1.push('');
    });
    lines.push(headers1.join(','));
    
    const headers2 = ['ranking'];
    Object.keys(rankingData).forEach(attrKey => {
        const attrData = rankingData[attrKey];
        headers2.push(attrData.name);
        headers2.push('team');
    });
    lines.push(headers2.join(','));
    
    // 为每一行创建数据
    for (let rowIndex = 0; rowIndex < maxRowCount; rowIndex++) {
        // 最左侧的rank列按照1、2、3、4的顺序显示
        const row = [rowIndex + 1];
        
        Object.keys(sortedData).forEach(attrKey => {
            const attrData = sortedData[attrKey];
            const rankedData = attrData[rowIndex];
            
            if (rankedData) {
                const value = formatValue(rankedData.value);
                const team = rankedData.team_no;
                
                // 检查是否有相同值，如果有则在CSV中添加等号标记
                const hasEqualValue = equalValueMap[attrKey] && equalValueMap[attrKey].has(rowIndex);
                row.push(hasEqualValue ? `${value}(=)` : value);
                row.push(hasEqualValue ? `${team}(=)` : team);
            } else {
                row.push('-');
                row.push('-');
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