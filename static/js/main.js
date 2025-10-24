const timezone = document.body.dataset.timezone || 'UTC';
const sessionTurnsCount = parseInt(document.body.dataset.sessionTurnsCount || '0');
const expertMode = document.body.dataset.expertMode === 'true';
const currentSessionId = document.body.dataset.currentSessionId;
const sessionData = JSON.parse(document.body.dataset.sessionData || '{}');


function isScrolledToBottom() {
    const turnsList = document.getElementById('turns-list-section');
    if (!turnsList) return false;
    // 少しの誤差を許容するための閾値（例: 1px）
    const threshold = 1;
    return turnsList.scrollHeight - turnsList.scrollTop - turnsList.clientHeight <= threshold;
}

document.addEventListener('DOMContentLoaded', function() {
    buildSessionTree();

    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true,
        });
    }

    function handleResponse(response) {
        // If the response is not OK, we need to parse the JSON body
        // to get the detailed error message from the server.
        if (!response.ok) {
            return response.json().then(errorData => {
                let errorMessage = `HTTP error! status: ${response.status}`;
                if (errorData && errorData.message) {
                    errorMessage = errorData.message;
                }
                if (errorData && errorData.details) {
                    errorMessage += `\n\n--- Details ---\n${errorData.details}`;
                }
                throw new Error(errorMessage);
            }).catch(parsingError => {
                // If parsing the error JSON fails, throw a generic error
                throw new Error(`HTTP error! status: ${response.status}. Could not parse error response.`);
            });
        }
        return response.json();
    }

    function forkSession(sessionId, forkIndex) {
        if (!confirm(`Are you sure you want to fork this session at turn index ${forkIndex}?`)) return;

        fetch(`/api/session/${sessionId}/fork/${forkIndex}`, { method: 'POST' })
            .then(handleResponse)
            .then(data => {
                if (data.success && data.new_session_id) {
                    window.location.href = `/session/${data.new_session_id}`;
                } else {
                    throw new Error(data.message || 'Failed to fork session.');
                }
            })
            .catch(handleError);
    }

    function handleError(error) {
        console.error('Error:', error);
        alert('An error occurred: ' + error.message);
    }

    function buildSessionTree() {
        const sessions = JSON.parse(document.body.dataset.sessions || '[]');
        const tree = {};

        // Build a tree structure from the flat list
        sessions.forEach(([id, meta]) => {
            const parts = id.split('/');
            let currentLevel = tree;
            parts.forEach((part, index) => {
                if (!currentLevel[part]) {
                    currentLevel[part] = { meta: null, children: {} };
                }
                if (index === parts.length - 1) {
                    currentLevel[part].meta = meta;
                    currentLevel[part].id = id;
                }
                currentLevel = currentLevel[part].children;
            });
        });

        const container = document.getElementById('session-list-container');
        if (container) {
            container.innerHTML = ''; // Clear existing
            const rootUl = createNode(tree, 0);
            container.appendChild(rootUl);
        }
    }

    function createNode(branch, level) {
        const ul = document.createElement('ul');
        if (level > 0) {
            ul.style.paddingLeft = '20px';
        }

        for (const key in branch) {
            const node = branch[key];
            const li = document.createElement('li');
            
            if (node.meta) {
                const a = document.createElement('a');
                a.href = `/session/${node.id}`;
                a.className = node.id === currentSessionId ? 'active' : '';
                a.innerHTML = `${node.meta.purpose} <span class="session-id">${node.id}</span>`;
                li.appendChild(a);
            }

            if (Object.keys(node.children).length > 0) {
                li.appendChild(createNode(node.children, level + 1));
            }
            ul.appendChild(li);
        }
        return ul;
    }

     function scrollToBottom() {
        const turnsList = document.getElementById('turns-list-section');
        if (turnsList) {
            turnsList.scrollTop = turnsList.scrollHeight;
        }
    }

    function renderMarkdown() {
        document.querySelectorAll('.model_response .turn-content, .compressed_history .turn-content').forEach(contentElement => {
            const rawMarkdownDiv = contentElement.querySelector('.raw-markdown');
            const renderedMarkdownDiv = contentElement.querySelector('.rendered-markdown');
            if (rawMarkdownDiv && renderedMarkdownDiv && window.marked) {
                renderedMarkdownDiv.innerHTML = marked.parse(rawMarkdownDiv.textContent || '');
            }
        });
    }

    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            return Promise.resolve();
        } catch (err) {
            return Promise.reject(err);
        } finally {
            document.body.removeChild(textArea);
        }
    }

    function deleteTurn(sessionId, turnIndex) {
        if (!confirm('Are you sure you want to delete this turn?')) return;
        fetch(`/api/session/${sessionId}/turn/${turnIndex}`, { method: 'DELETE' })
            .then(handleResponse)
            .then(data => data.success ? window.location.reload() : Promise.reject(new Error(data.message)))
            .catch(handleError);
    }

    function deleteSession(sessionId) {
        if (!confirm('Are you sure you want to delete this entire session?')) return;
        fetch(`/api/session/${sessionId}`, { method: 'DELETE' })
            .then(handleResponse)
            .then(data => data.success ? (window.location.href = '/') : Promise.reject(new Error(data.message)))
            .catch(handleError);
    }

    function toggleEdit(editButton, sessionId, turnIndex, turnType) {
        const turnElement = document.getElementById(`turn-${turnIndex}`);
        const contentDiv = turnElement.querySelector('.turn-content');
        const controls = editButton.parentElement;

        let editableElement, originalContent, fieldName;
        
        if (turnType === 'model_response' || turnType === 'condensed_history') {
            editableElement = contentDiv.querySelector('.rendered-markdown');
            originalContent = contentDiv.querySelector('.raw-markdown').textContent.trim();
            fieldName = 'content';
        } else { // user_task
            editableElement = contentDiv.querySelector('.editable');
            originalContent = editableElement.textContent.trim();
            fieldName = 'instruction';
        }

        const textarea = document.createElement('textarea');
        textarea.value = originalContent;
        textarea.style.width = '100%';
        textarea.style.minHeight = '120px';
        textarea.style.height = (editableElement.scrollHeight + 20) + 'px';
        textarea.style.boxSizing = 'border-box';
        textarea.style.padding = '10px';
        textarea.style.borderRadius = '5px';
        textarea.style.border = '1px solid #ced4da';
        textarea.style.whiteSpace = 'pre-wrap';
        textarea.style.wordWrap = 'break-word';

        editableElement.style.display = 'none';
        if (editableElement.previousElementSibling) editableElement.previousElementSibling.style.display = 'none';
        
        contentDiv.appendChild(textarea);
        textarea.focus();

        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        const saveButton = document.createElement('button');
        saveButton.className = 'action-btn save-btn';
        saveButton.textContent = 'Save';
        saveButton.onclick = () => saveEdit(sessionId, turnIndex, fieldName, textarea.value, () => exitEditMode(editButton, contentDiv, textarea, controls));

        const cancelButton = document.createElement('button');
        cancelButton.className = 'action-btn cancel-btn';
        cancelButton.textContent = 'Cancel';
        cancelButton.onclick = () => exitEditMode(editButton, contentDiv, textarea, controls);

        const buttonContainer = document.createElement('div');
        buttonContainer.style.textAlign = 'right';
        buttonContainer.appendChild(saveButton);
        buttonContainer.appendChild(cancelButton);

        controls.style.visibility = 'hidden';
        controls.parentElement.appendChild(buttonContainer);
    }

    function exitEditMode(editButton, contentDiv, textarea, controls) {
        const editableElement = contentDiv.querySelector('.editable');
        editableElement.style.display = 'block';
        
        textarea.remove();
        const buttonContainer = controls.parentElement.querySelector('div[style="text-align: right;"]');
        if (buttonContainer) buttonContainer.remove();
        
        controls.style.visibility = 'visible';
    }

    function saveEdit(sessionId, turnIndex, fieldName, newContent, callback) {
        const payload = { [fieldName]: newContent };

        fetch(`/api/session/${sessionId}/turn/${turnIndex}/edit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
            .then(handleResponse)
            .then(data => {
                if (data.success) {
                    const turnElement = document.getElementById(`turn-${turnIndex}`);
                    const turnType = turnElement.classList.contains('model_response') || turnElement.classList.contains('condensed_history') ? 'model_response' : 'user_task';
                    
                    if (turnType === 'model_response') {
                        const renderedDiv = turnElement.querySelector('.rendered-markdown');
                        const rawDiv = turnElement.querySelector('.raw-markdown');
                        rawDiv.textContent = newContent;
                        if(window.marked) {
                            renderedDiv.innerHTML = marked.parse(newContent);
                        }
                    } else {
                        turnElement.querySelector('.editable').textContent = newContent;
                    }
                    callback();
                } else { throw new Error(data.message); }
            })
            .catch(handleError);
    }

    function saveMetaEdit(sessionId) {
        const viewContainer = document.getElementById('session-meta-view');
        const payload = {
            purpose: viewContainer.querySelector('[data-field="purpose"]').value,
            background: viewContainer.querySelector('[data-field="background"]').value,
            roles: viewContainer.querySelector('[data-field="roles"]').value.split(',').map(s => s.trim()).filter(Boolean),
            multi_step_reasoning_enabled: viewContainer.querySelector('[data-field="multi_step_reasoning_enabled"]').checked,
            hyperparameters: {
                temperature: { value: parseFloat(viewContainer.querySelector('[data-field="temperature"]').value) },
                top_p: { value: parseFloat(viewContainer.querySelector('[data-field="top_p"]').value) },
                top_k: { value: parseInt(viewContainer.querySelector('[data-field="top_k"]').value, 10) }
            }
        };

        fetch(`/api/session/${sessionId}/meta/edit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
            .then(handleResponse)
            .then(data => {
                if (data.success) {
                    alert('Session meta saved successfully!');
                    window.location.reload();
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(handleError);
    }

    function sendInstruction(sessionId) {
        const instructionTextarea = document.getElementById('new-instruction-text');
        const instruction = instructionTextarea.value.trim();
        if (!instruction) return alert('Instruction cannot be empty.');

        const sendButton = document.querySelector('.send-instruction-btn');
        sendButton.disabled = true;
        const originalButtonText = sendButton.textContent;
        sendButton.textContent = 'Sending...';

        const turnsList = document.getElementById('turns-list-section');
        
        const now = new Date();
        const timestamp = new Intl.DateTimeFormat('sv-SE', {
            timeZone: timezone,
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        }).format(now);

        // 1. Create and insert the user's turn immediately
        const userTurnNumber = sessionTurnsCount + 1;
        const userTurnPlaceholder = document.createElement('div');
        userTurnPlaceholder.className = 'turn user_task';
        userTurnPlaceholder.innerHTML = `
            <div class="turn-header">
                <span>
                    <strong style="color: #007bff; margin-right: 10px;">${userTurnNumber}:</strong>
                    You
                    <span style="font-weight: normal; color: #999; margin-left: 10px;">${timestamp}</span>
                </span>
            </div>
            <div class="turn-content">
                <pre>${instruction}</pre>
            </div>
        `;

        turnsList.appendChild(userTurnPlaceholder);
        scrollToBottom();
        
        // 2. Create and insert the placeholder for the model's response
        const modelTurnNumber = sessionTurnsCount + 2;
        const modelTurnPlaceholder = document.createElement('div');
        modelTurnPlaceholder.className = 'turn model_response';
        modelTurnPlaceholder.innerHTML = `
            <div class="turn-header">
                <span>
                    <strong style="color: #007bff; margin-right: 10px;">${modelTurnNumber}:</strong>
                    Model
                    <span style="font-weight: normal; color: #999; margin-left: 10px;">${timestamp}</span>
                </span>
            </div>
            <div class="turn-content">
                <div class="rendered-markdown markdown-body"></div>
            </div>
        `;
        turnsList.appendChild(modelTurnPlaceholder);
        const responseContainer = modelTurnPlaceholder.querySelector('.rendered-markdown');                    
        setTimeout(() => {
            scrollToBottom();
        }, 1000);

        // 3. Clear the input and start the fetch
        instructionTextarea.value = '';
        let fullResponse = '';

        fetch(`/api/session/${sessionId}/instruction`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instruction })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            function processStream() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        fetchAndReplaceTurns(sessionId, userTurnNumber - 1, [userTurnPlaceholder, modelTurnPlaceholder]);
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    
                    let boundary = buffer.indexOf('\n\n');
                    while (boundary !== -1) {
                        const message = buffer.substring(0, boundary);
                        buffer = buffer.substring(boundary + 2);

                        if (message.startsWith('event: end')) {
                            reader.cancel();
                            fetchAndReplaceTurns(sessionId, userTurnNumber - 1, [userTurnPlaceholder, modelTurnPlaceholder]);
                            return;
                        }
                        
                        if (message.startsWith('data:')) {
                            try {
                                const data = JSON.parse(message.substring(5));
                                if (data.content) {
                                    fullResponse += data.content;
                                    responseContainer.innerHTML = marked.parse(fullResponse);
                                }
                                if (data.error) {
                                    responseContainer.innerHTML = `<p style="color: red;"><strong>Error:</strong></p><pre>${data.error}</pre>`;
                                    sendButton.disabled = false;
                                    sendButton.textContent = originalButtonText;
                                    reader.cancel();
                                    // Remove the placeholders on error
                                    userTurnPlaceholder.remove();
                                    modelTurnPlaceholder.remove();
                                    return;
                                }
                            } catch (e) {
                                console.error("Failed to parse stream data:", e);
                            }
                        }
                        boundary = buffer.indexOf('\n\n');

                        if (isScrolledToBottom()) {
                            scrollToBottom();
                        }
                    }
                    processStream();
                }).catch(error => {
                    handleError(error);
                    sendButton.disabled = false;
                    sendButton.textContent = originalButtonText;
                });
            }
            processStream();
        })
        .catch(error => {
            handleError(error);
            sendButton.disabled = false;
            sendButton.textContent = originalButtonText;
        });
    }

    function createTurnElement(turn, index, expertMode) {
        const turnElement = document.createElement('div');
        turnElement.className = `turn ${turn.type}`;
        turnElement.id = `turn-${index}`;

        const timestamp = turn.timestamp ? turn.timestamp.replace('T', ' ').split('.')[0] : '';
        
        let headerContent = '';
        if (turn.type === 'user_task') headerContent = 'You';
        else if (turn.type === 'model_response') headerContent = 'Model';
        else if (turn.type === 'function_calling') headerContent = 'Function Calling';
        else if (turn.type === 'tool_response') headerContent = 'Tool Response';
        else if (turn.type === 'compressed_history') headerContent = 'Compressed';
        else headerContent = 'Unknown';

        let turnContentHTML = '';
        if (turn.type === 'user_task') {
            turnContentHTML = `<pre class="editable" data-field="instruction">${turn.instruction}</pre>`;
        } else if (turn.type === 'model_response' || turn.type === 'compressed_history') {
            const compressedPrefix = turn.type === 'compressed_history' ? `<p><strong><em>-- History Compressed --</em></strong></p>` : '';
            turnContentHTML = `
                ${compressedPrefix}
                <div class="raw-markdown" style="display: none;">${turn.content}</div>
                <div class="rendered-markdown markdown-body editable" data-field="content">${marked.parse(turn.content || '')}</div>
            `;
        } else if (turn.type === 'function_calling') {
            turnContentHTML = `<pre>${turn.response}</pre>`;
        } else if (turn.type === 'tool_response') {
            turnContentHTML = `
                <div class="tool-response-content">
                    <strong>Status: </strong>
                    <span class="status-${turn.response.status}">${turn.response.status}</span>
                </div>
            `;
        }

        let controlsHTML = '';
        if (expertMode) {
            if (turn.type === 'model_response') {
                 controlsHTML += `<button class="action-btn fork-btn" data-session-id="${currentSessionId}" data-fork-index="${index}">Fork</button>`;
            }
            controlsHTML += `
                <button class="action-btn copy-turn-btn" data-turn-index="${index}">Copy</button>
                <button class="action-btn edit-btn" data-session-id="${currentSessionId}" data-turn-index="${index}" data-turn-type="${turn.type}">Edit</button>
                <button class="action-btn delete-btn" data-session-id="${currentSessionId}" data-turn-index="${index}">Delete</button>
            `;
        } else {
             if (turn.type === 'model_response') {
                 controlsHTML += `<button class="action-btn fork-btn" data-session-id="${currentSessionId}" data-fork-index="${index}">Fork</button>`;
            }
            controlsHTML += `<button class="action-btn copy-turn-btn" data-turn-index="${index}">Copy</button>`;
        }


        turnElement.innerHTML = `
            <div class="turn-header">
                <span>
                    <strong style="color: #007bff; margin-right: 10px;">${index + 1}:</strong>
                    ${headerContent}
                    <span style="font-weight: normal; color: #999; margin-left: 10px;">${timestamp}</span>
                </span>
                <div class="turn-header-controls">${controlsHTML}</div>
            </div>
            <div class="turn-content">${turnContentHTML}</div>
        `;
        return turnElement;
    }

     function fetchAndReplaceTurns(sessionId, startIndex, placeholders) {
        fetch(`/api/session/${sessionId}/turns?since=${startIndex}`)
            .then(handleResponse)
            .then(data => {
                if (data.success && data.turns.length > 0) {
                    // Clear placeholders
                    placeholders.forEach(p => p.remove());

                    const turnsList = document.getElementById('turns-list-section');

                    data.turns.forEach((turn, i) => {
                        const turnIndex = startIndex + i;
                        const newTurnElement = createTurnElement(turn, turnIndex, expertMode);
                        turnsList.appendChild(newTurnElement);
                    });

                    // Re-attach event listeners to new buttons
                    attachEventListenersToTurns();
                    scrollToBottom();
                }
            })
            .catch(handleError)
            .finally(() => {
                const sendButton = document.querySelector('.send-instruction-btn');
                sendButton.disabled = false;
                sendButton.textContent = 'Send Instruction';
            });
    }

    function attachEventListenersToTurns() {
        // This is a simplified version. You might need to re-run the specific listener attachments
        // if they are complex. For this case, let's re-run the querySelectors.
         document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function() {
                const { sessionId, turnIndex, turnType } = this.dataset;
                toggleEdit(this, sessionId, parseInt(turnIndex), turnType);
            });
        });

        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', function() {
                const { sessionId, turnIndex } = this.dataset;
                deleteTurn(sessionId, parseInt(turnIndex));
            });
        });
         document.querySelectorAll('.fork-btn').forEach(button => {
            button.addEventListener('click', function() {
                const sessionId = this.dataset.sessionId;
                const forkIndex = this.dataset.forkIndex;
                forkSession(sessionId, parseInt(forkIndex));
            });
        });

        document.querySelectorAll('.copy-turn-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                const turnIndex = this.dataset.turnIndex;
                const turnElement = document.getElementById(`turn-${turnIndex}`);
                const turnType = turnElement.classList.contains('model_response') ? 'model_response' :
                                     (turnElement.classList.contains('condensed_history') ? 'condensed_history' : 'user_task');

                let textToCopy = '';
                if (turnType === 'model_response' || turnType === 'condensed_history') {
                    textToCopy = turnElement.querySelector('.raw-markdown').textContent;
                } else { // user_task
                    textToCopy = turnElement.querySelector('.editable').textContent;
                }

                const copyPromise = navigator.clipboard ? 
                    navigator.clipboard.writeText(textToCopy) : 
                    fallbackCopyTextToClipboard(textToCopy);

                copyPromise.then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy turn content: ', err);
                    alert('Failed to copy');
                });
            });
        });
    }

    // Initial page load setup
    renderMarkdown();
    attachEventListenersToTurns();
    scrollToBottom();

    // Update hyperparameter value displays on slider input
    document.querySelectorAll('input[type="range"][data-field]').forEach(slider => {
        const valueSpan = document.getElementById(`edit-${slider.dataset.field}-value`);
        if (valueSpan) {
            slider.addEventListener('input', (event) => {
                valueSpan.textContent = event.target.value;
            });
        }
    });
    
    document.getElementById('new-chat-button').addEventListener('click', () => window.location.href = '/new_session');
    
    document.getElementById('save-meta-btn')?.addEventListener('click', function() {
        saveMetaEdit(this.dataset.sessionId);
    });

    document.querySelectorAll('.delete-session-btn, .send-instruction-btn').forEach(button => {
        button.addEventListener('click', function() {
            const actionMap = { 'delete-session-btn': deleteSession, 'send-instruction-btn': sendInstruction };
            const action = Object.keys(actionMap).find(cls => this.classList.contains(cls));
            if(action) actionMap[action](this.dataset.sessionId);
        });
    });

    const newInstructionText = document.getElementById('new-instruction-text');
    if (newInstructionText) newInstructionText.focus();

    document.getElementById('todos-list')?.addEventListener('change', function(event) {
        if (event.target.classList.contains('todo-checkbox')) {
            const checkbox = event.target;
            const index = parseInt(checkbox.dataset.index, 10);
            const sessionId = document.getElementById('current-session-id').value;
            let todos = sessionData.todos || [];
            if (todos[index]) {
                todos[index].checked = checkbox.checked;
            }
            saveTodos(sessionId, todos);
        }
    });

    function saveTodos(sessionId, todos) {
        const payload = { todos };

        fetch(`/api/session/${sessionId}/todos/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(handleResponse)
        .then(data => {
            if (!data.success) {
                throw new Error(data.message);
            }
            console.log("Todos saved successfully.");
        })
        .catch(error => {
            handleError(error);
        });
    }

    document.getElementById('references-list')?.addEventListener('change', function(event) {
        if (event.target.classList.contains('reference-checkbox')) {
            const sessionId = document.getElementById('current-session-id').value;
            let references = sessionData.references || [];
            const checkbox = event.target;
            const index = parseInt(checkbox.dataset.index, 10);
            if (references[index]) {
                references[index].disabled = !checkbox.checked;
            }
            const label = checkbox.closest('label');
            const span = label.querySelector('span');
            if (checkbox.checked) {
                span.style.textDecoration = 'none';
                span.style.color = 'inherit';
            } else {
                span.style.textDecoration = 'line-through';
                span.style.color = '#888';
            }
            saveReferences(sessionId, references);
        }
    });

    document.getElementById('toggle-references-btn')?.addEventListener('click', function() {
        const sessionId = document.getElementById('current-session-id').value;
        let references = sessionData.references || [];
        const shouldCheckAll = references.some(ref => ref.disabled);
        references.forEach(ref => ref.disabled = !shouldCheckAll);
        saveReferences(sessionId, references, true); // Pass true to reload
    });

    function saveReferences(sessionId, references, reload = false) {
        const payload = { references };

        fetch(`/api/session/${sessionId}/references/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(handleResponse)
        .then(data => {
            if (!data.success) {
                throw new Error(data.message);
            }
            console.log("References saved successfully.");
            if (reload) {
                window.location.reload();
            }
        })
        .catch(error => {
            handleError(error);
            window.location.reload();
        });
    }
});
