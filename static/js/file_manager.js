// 文件管理页面的JavaScript逻辑
let currentFiles = [];
let selectedFiles = new Set();
let showTrashFiles = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initFileManager();
});

// 初始化文件管理器
function initFileManager() {
    // 绑定显示回收站文件的开关
    const showTrashCheckbox = document.getElementById('showTrashFiles');
    showTrashCheckbox.addEventListener('change', function() {
        showTrashFiles = this.checked;
        updateToolbarButtons();
        refreshFiles();
    });

    // 初始加载文件列表
    refreshFiles();
}

// 刷新文件列表
function refreshFiles() {
    showLoading();
    
    const includeTrash = showTrashFiles ? 'true' : 'false';
    fetch(`/api/files?include_trash=${includeTrash}`)
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                currentFiles = data.files;
                displayFiles(currentFiles);
                updateFileCount(currentFiles.length);
                clearSelection();
            } else {
                showError(data.message || '获取文件列表失败');
            }
        })
        .catch(error => {
            showLoading(false);
            showError('网络错误: ' + error.message);
        });
}

// 显示文件列表
function displayFiles(files) {
    const tableBody = document.getElementById('fileTableBody');
    const emptyState = document.getElementById('emptyState');
    
    if (files.length === 0) {
        tableBody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    tableBody.innerHTML = files.map(file => `
        <tr>
            <td>
                <input type="checkbox" class="file-checkbox" 
                       value="${file.filename}" 
                       onchange="toggleFileSelection('${file.filename}')">
            </td>
            <td>
                <span class="text-truncate d-inline-block" style="max-width: 200px;" 
                      title="${file.filename}">
                    ${file.filename}
                </span>
            </td>
            <td>${file.event_code}</td>
            <td>${file.team_no}</td>
            <td>
                <span class="badge ${getTournamentLevelClass(file.tournament_level)}">
                    ${file.tournament_level}
                </span>
            </td>
            <td>${file.match_no}</td>
            <td>${formatTimestamp(file.timestamp)}</td>
            <td>
                <span class="badge ${file.status === 'active' ? 'bg-success' : 'bg-warning'}">
                    ${file.status === 'active' ? '活跃' : '回收站'}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    ${file.status === 'active' ? `
                        <button class="btn btn-outline-warning" 
                                onclick="moveToTrashSingle('${file.filename}')"
                                title="移到回收站">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : `
                        <button class="btn btn-outline-success" 
                                onclick="restoreFromTrashSingle('${file.filename}')"
                                title="恢复">
                            <i class="fas fa-undo"></i>
                        </button>
                        <button class="btn btn-outline-danger" 
                                onclick="permanentlyDeleteSingle('${file.filename}')"
                                title="永久删除">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    `}
                </div>
            </td>
        </tr>
    `).join('');
}

// 获取赛制等级的CSS类
function getTournamentLevelClass(level) {
    switch(level) {
        case 'Practice': return 'bg-secondary';
        case 'Qualification': return 'bg-primary';
        case 'Playoff': return 'bg-warning text-dark';
        default: return 'bg-secondary';
    }
}

// 格式化时间戳
function formatTimestamp(timestamp) {
    const date = new Date(parseInt(timestamp));
    if (isNaN(date.getTime())) {
        // 如果时间戳解析失败，尝试作为字符串解析
        const str = timestamp.toString();
        if (str.length === 14) {
            // 格式：YYYYMMDD_HHMMSS
            const year = str.substring(0, 4);
            const month = str.substring(4, 6);
            const day = str.substring(6, 8);
            const hour = str.substring(8, 10);
            const minute = str.substring(10, 12);
            const second = str.substring(12, 14);
            return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
        }
        return timestamp;
    }
    return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN');
}

// 切换文件选择状态
function toggleFileSelection(filename) {
    if (selectedFiles.has(filename)) {
        selectedFiles.delete(filename);
    } else {
        selectedFiles.add(filename);
    }
    updateSelectionUI();
}

// 全选切换
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');
    
    if (selectAllCheckbox.checked) {
        fileCheckboxes.forEach(cb => {
            cb.checked = true;
            selectedFiles.add(cb.value);
        });
    } else {
        fileCheckboxes.forEach(cb => {
            cb.checked = false;
            selectedFiles.delete(cb.value);
        });
    }
    updateSelectionUI();
}

// 全选
function selectAll() {
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');
    fileCheckboxes.forEach(cb => {
        cb.checked = true;
        selectedFiles.add(cb.value);
    });
    document.getElementById('selectAllCheckbox').checked = true;
    updateSelectionUI();
}

// 清空选择
function clearSelection() {
    selectedFiles.clear();
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');
    fileCheckboxes.forEach(cb => cb.checked = false);
    document.getElementById('selectAllCheckbox').checked = false;
    updateSelectionUI();
}

// 更新选择UI
function updateSelectionUI() {
    const selectedCount = selectedFiles.size;
    const batchToolbar = document.getElementById('batchToolbar');
    const selectedCountElement = document.getElementById('selectedCount');
    
    if (selectedCount > 0) {
        batchToolbar.style.display = 'block';
        selectedCountElement.textContent = `已选择 ${selectedCount} 个文件`;
        updateToolbarButtons();
    } else {
        batchToolbar.style.display = 'none';
    }
}

// 更新工具栏按钮状态
function updateToolbarButtons() {
    const moveToTrashBtn = document.getElementById('moveToTrashBtn');
    const restoreBtn = document.getElementById('restoreBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    
    if (showTrashFiles) {
        // 显示回收站文件时，显示恢复和永久删除按钮
        moveToTrashBtn.style.display = 'none';
        restoreBtn.style.display = 'inline-block';
        deleteBtn.style.display = 'inline-block';
    } else {
        // 显示活跃文件时，显示移到回收站按钮
        moveToTrashBtn.style.display = 'inline-block';
        restoreBtn.style.display = 'none';
        deleteBtn.style.display = 'none';
    }
}

// 移动到回收站（批量）
function moveToTrash() {
    if (selectedFiles.size === 0) {
        showError('请选择要移动的文件');
        return;
    }
    
    const filenames = Array.from(selectedFiles);
    showConfirmModal(
        '确认移动到回收站',
        `确定要将 ${filenames.length} 个文件移动到回收站吗？`,
        () => performMoveToTrash(filenames)
    );
}

// 单个文件移动到回收站
function moveToTrashSingle(filename) {
    showConfirmModal(
        '确认移动到回收站',
        `确定要将文件 "${filename}" 移动到回收站吗？`,
        () => performMoveToTrash([filename])
    );
}

// 执行移动到回收站操作
function performMoveToTrash(filenames) {
    showLoading();
    
    fetch('/api/files/move-to-trash', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filenames: filenames })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showSuccess(data.message);
            refreshFiles();
            
            if (data.errors && data.errors.length > 0) {
                showError('部分文件操作失败：\n' + data.errors.join('\n'));
            }
        } else {
            showError(data.message || '移动到回收站失败');
        }
    })
    .catch(error => {
        showLoading(false);
        showError('网络错误: ' + error.message);
    });
}

// 从回收站恢复（批量）
function restoreFromTrash() {
    if (selectedFiles.size === 0) {
        showError('请选择要恢复的文件');
        return;
    }
    
    const filenames = Array.from(selectedFiles);
    showConfirmModal(
        '确认恢复文件',
        `确定要恢复 ${filenames.length} 个文件吗？`,
        () => performRestore(filenames)
    );
}

// 单个文件恢复
function restoreFromTrashSingle(filename) {
    showConfirmModal(
        '确认恢复文件',
        `确定要恢复文件 "${filename}" 吗？`,
        () => performRestore([filename])
    );
}

// 执行恢复操作
function performRestore(filenames) {
    showLoading();
    
    fetch('/api/files/restore', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filenames: filenames })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showSuccess(data.message);
            refreshFiles();
            
            if (data.errors && data.errors.length > 0) {
                showError('部分文件操作失败：\n' + data.errors.join('\n'));
            }
        } else {
            showError(data.message || '恢复文件失败');
        }
    })
    .catch(error => {
        showLoading(false);
        showError('网络错误: ' + error.message);
    });
}

// 永久删除（批量）
function permanentlyDelete() {
    if (selectedFiles.size === 0) {
        showError('请选择要删除的文件');
        return;
    }
    
    const filenames = Array.from(selectedFiles);
    showConfirmModal(
        '确认永久删除',
        `⚠️ 警告：确定要永久删除 ${filenames.length} 个文件吗？此操作不可恢复！`,
        () => performPermanentDelete(filenames)
    );
}

// 单个文件永久删除
function permanentlyDeleteSingle(filename) {
    showConfirmModal(
        '确认永久删除',
        `⚠️ 警告：确定要永久删除文件 "${filename}" 吗？此操作不可恢复！`,
        () => performPermanentDelete([filename])
    );
}

// 执行永久删除操作
function performPermanentDelete(filenames) {
    showLoading();
    
    fetch('/api/files/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filenames: filenames })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showSuccess(data.message);
            refreshFiles();
            
            if (data.errors && data.errors.length > 0) {
                showError('部分文件操作失败：\n' + data.errors.join('\n'));
            }
        } else {
            showError(data.message || '永久删除失败');
        }
    })
    .catch(error => {
        showLoading(false);
        showError('网络错误: ' + error.message);
    });
}

// 显示确认对话框
function showConfirmModal(title, message, onConfirm) {
    const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    const titleElement = document.getElementById('confirmModalTitle');
    const bodyElement = document.getElementById('confirmModalBody');
    const confirmBtn = document.getElementById('confirmBtn');
    
    titleElement.textContent = title;
    bodyElement.textContent = message;
    
    // 清除之前的事件监听器
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    // 添加新的事件监听器
    newConfirmBtn.addEventListener('click', function() {
        modal.hide();
        onConfirm();
    });
    
    modal.show();
}

// 更新文件数量显示
function updateFileCount(count) {
    document.getElementById('fileCount').textContent = count;
} 