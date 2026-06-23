/**
 * DbAgent Web Interface — Main JavaScript
 *
 * Handles:
 * - Sending queries to the API
 * - Displaying messages (chat-like)
 * - Showing results in a table
 * - Connection status checking
 * - Keyboard shortcuts
 */
(function () {
    'use strict';

    // --- DOM references ---
    const $id = (id) => document.getElementById(id);
    const $sel = (sel) => document.querySelector(sel);

    const messagesEl = $id('messages');
    const queryInput = $id('query-input');
    const btnSend = $id('btn-send');
    const btnCheck = $id('btn-check');
    const btnPull = $id('btn-pull');
    const btnClear = $id('btn-clear');
    const btnCloseResults = $id('btn-close-results');
    const loadingOverlay = $id('loading-overlay');
    const loadingText = $id('loading-text');
    const resultsPanel = $id('results-panel');
    const resultsThead = $id('results-thead');
    const resultsTbody = $id('results-tbody');
    const chatArea = $id('chat-area');

    const ollamaDot = $sel('#ollama-status .status-dot');
    const ollamaLabel = $sel('#ollama-status .status-label');
    const dbDot = $sel('#db-status .status-dot');
    const dbLabel = $sel('#db-status .status-label');
    const modelLabel = $id('model-status');

    let isProcessing = false;

    // --- API helpers ---
    async function apiPost(url, body) {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            const text = await resp.text();
            throw new Error('HTTP ' + resp.status + ': ' + text.slice(0, 200));
        }
        return resp.json();
    }

    async function apiGet(url) {
        const resp = await fetch(url);
        if (!resp.ok) {
            const text = await resp.text();
            throw new Error('HTTP ' + resp.status + ': ' + text.slice(0, 200));
        }
        return resp.json();
    }

    // --- Message helpers ---
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function addMessage(html, className = '') {
        const div = document.createElement('div');
        div.className = 'message' + (className ? ' ' + className : '');
        div.innerHTML = '<div class="msg-content">' + html + '</div>';
        messagesEl.appendChild(div);
        scrollToBottom();
    }

    function addUserMessage(text) {
        addMessage(escapeHtml(text), 'user');
    }

    function addStepMessage(number, label, color) {
        const html = '<span style="color:' + color + '; font-size:16px;">●</span> <strong>Шаг ' + number + ':</strong> <span style="color:' + color + ';">' + label + '</span>';
        addMessage(html, 'step step-' + number.charAt(0));
    }

    function addSqlMessage(sql) {
        addMessage('<span style="color:#f9e2af;">SQL:</span>\n' + escapeHtml(sql), 'sql');
    }

    function addSummaryMessage(text) {
        addMessage(text.replace(/\n/g, '<br>'), 'summary');
    }

    function addErrorMessage(text) {
        addMessage('⚠ ' + text.replace(/\n/g, '<br>'), 'error');
    }

    function addInfoMessage(text) {
        addMessage(text, 'info');
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    // --- Results table ---
    function showResults(columnNames, rows, totalRows) {
        // Clear previous
        resultsThead.innerHTML = '';
        resultsTbody.innerHTML = '';

        // Header
        var tr = document.createElement('tr');
        for (var i = 0; i < columnNames.length; i++) {
            var th = document.createElement('th');
            th.textContent = columnNames[i];
            tr.appendChild(th);
        }
        resultsThead.appendChild(tr);

        // Body
        for (var r = 0; r < rows.length; r++) {
            var row = rows[r];
            tr = document.createElement('tr');
            for (var c = 0; c < row.length; c++) {
                var td = document.createElement('td');
                td.textContent = row[c] !== null ? String(row[c]) : 'NULL';
                tr.appendChild(td);
            }
            resultsTbody.appendChild(tr);
        }

        var infoText = '📊 Получено строк: ' + totalRows;
        if (totalRows > 5) {
            infoText += ' (показаны первые 5)';
        }
        addInfoMessage(infoText);

        resultsPanel.classList.remove('hidden');
    }

    // --- Query processing ---
    async function sendQuery() {
        var query = queryInput.value.trim();
        if (!query || isProcessing) return;

        isProcessing = true;
        queryInput.value = '';
        queryInput.disabled = true;
        btnSend.disabled = true;
        loadingOverlay.classList.remove('hidden');
        loadingText.textContent = 'Выполняю запрос...';
        resultsPanel.classList.add('hidden');

        addUserMessage(query);

        try {
            // Step 1
            addStepMessage('1/3', 'Генерирую SQL-запрос...', '#89b4fa');
            loadingText.textContent = 'Шаг 1/3: генерация SQL...';

            var rawResp = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query }),
            });
            if (!rawResp.ok) {
                var errText = await rawResp.text();
                throw new Error('HTTP ' + rawResp.status + ': ' + errText.slice(0, 300));
            }
            var data = await rawResp.json();

            if (data.error) {
                addErrorMessage(data.error);
                finishQuery();
                return;
            }

            // SQL generated
            addSqlMessage(data.sql);

            // Step 2
            addStepMessage('2/3', 'Выполняю SQL-запрос к БД...', '#f9e2af');
            loadingText.textContent = 'Шаг 2/3: выполнение SQL...';

            // Results
            if (data.column_names && data.rows) {
                showResults(data.column_names, data.rows, data.total_rows);
            }

            // Step 3
            addStepMessage('3/3', 'Суммаризирую результат...', '#a6e3a1');
            loadingText.textContent = 'Шаг 3/3: суммаризация...';

            // Summary
            if (data.summary) {
                addSummaryMessage(data.summary);
            }

            loadingText.textContent = '✅ Готово';
            setTimeout(function () {
                loadingOverlay.classList.add('hidden');
            }, 500);

        } catch (err) {
            addErrorMessage('Ошибка: ' + err.message);
            console.error(err);
            loadingOverlay.classList.add('hidden');
        } finally {
            finishQuery();
        }
    }

    function finishQuery() {
        isProcessing = false;
        queryInput.disabled = false;
        btnSend.disabled = false;
        queryInput.focus();
    }

    // --- Connection status ---
    async function checkStatus() {
        ollamaDot.className = 'status-dot yellow';
        ollamaLabel.textContent = 'Ollama: проверка...';
        dbDot.className = 'status-dot yellow';
        dbLabel.textContent = 'PostgreSQL: проверка...';

        try {
            var status = await apiGet('/api/status');
            if (status.ollama) {
                ollamaDot.className = 'status-dot green';
                ollamaLabel.textContent = 'Ollama: доступен';
                if (status.model_name) {
                    modelLabel.textContent = '🤖 Модель: ' + status.model_name;
                }
            } else {
                ollamaDot.className = 'status-dot red';
                ollamaLabel.textContent = 'Ollama: недоступен';
            }
            if (status.db) {
                dbDot.className = 'status-dot green';
                dbLabel.textContent = 'PostgreSQL: подключена';
            } else {
                dbDot.className = 'status-dot red';
                dbLabel.textContent = 'PostgreSQL: ошибка';
            }
        } catch (err) {
            ollamaDot.className = 'status-dot red';
            ollamaLabel.textContent = 'Ollama: ошибка';
            dbDot.className = 'status-dot red';
            dbLabel.textContent = 'PostgreSQL: ошибка';
            console.error(err);
        }
    }

    // --- Pull model ---
    async function pullModel() {
        if (isProcessing) return;
        addInfoMessage('⏳ Загрузка модели Ollama, пожалуйста подождите...');
        try {
            var result = await apiPost('/api/pull-model', {});
            if (result.success) {
                addInfoMessage('✅ Модель успешно загружена.');
            } else {
                addErrorMessage('Не удалось загрузить модель Ollama.');
            }
        } catch (err) {
            addErrorMessage('Ошибка при загрузке модели: ' + err.message);
            console.error(err);
        }
    }

    // --- Clear conversation ---
    function clearConversation() {
        var msgs = messagesEl.querySelectorAll('.message:not(.welcome)');
        for (var i = 0; i < msgs.length; i++) {
            msgs[i].remove();
        }
        resultsPanel.classList.add('hidden');
    }

    // --- Event listeners ---
    btnSend.addEventListener('click', sendQuery);
    queryInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    });

    btnCheck.addEventListener('click', checkStatus);
    btnPull.addEventListener('click', pullModel);
    btnClear.addEventListener('click', clearConversation);
    btnCloseResults.addEventListener('click', function () {
        resultsPanel.classList.add('hidden');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && (e.key === 'r' || e.key === 'R')) {
            e.preventDefault();
            checkStatus();
        }
        if (e.ctrlKey && (e.key === 'l' || e.key === 'L')) {
            e.preventDefault();
            clearConversation();
        }
    });

    // --- Initialization ---
    checkStatus();

})();