document.addEventListener('DOMContentLoaded', () => {
    // 1. Fetch Drops
    fetchData('db_drops.json', 'feed-drops', renderDropCard);
    
    // 2. Fetch Tips
    fetchData('db_tips.json', 'feed-tips', renderTipCard);
    
    // 3. Fetch Prompts
    fetchData('db_prompts.json', 'feed-prompts', renderPromptCard);
});

async function fetchData(url, containerId, renderFunction) {
    const container = document.getElementById(containerId);
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        container.innerHTML = ''; // Clear loader
        
        if (data.length === 0) {
            container.innerHTML = '<div class="card"><p class="card-content">No data yet. Check back soon!</p></div>';
            return;
        }

        data.forEach(item => {
            const cardHTML = renderFunction(item);
            container.insertAdjacentHTML('beforeend', cardHTML);
        });

        // Add copy listeners for Prompts
        if (containerId === 'feed-prompts') {
            attachCopyListeners(container);
        }

    } catch (error) {
        console.error('Error fetching data:', error);
        container.innerHTML = '<div class="card"><p class="card-content" style="color: #ef4444;">No content generated yet. Check back tomorrow!</p></div>';
    }
}

function renderDropCard(item) {
    let itemsHTML = '';
    if (item.items && Array.isArray(item.items)) {
        item.items.forEach(tool => {
            itemsHTML += `
                <div class="drop-item">
                    <div class="drop-item-title">${tool.title}</div>
                    <div class="card-content">${tool.description}</div>
                </div>
            `;
        });
    }

    return `
        <div class="card">
            <div class="card-date">${item.date}</div>
            ${itemsHTML}
        </div>
    `;
}

function renderTipCard(item) {
    let itemsHTML = '';
    if (item.items && Array.isArray(item.items)) {
        item.items.forEach(tip => {
            itemsHTML += `
                <div class="drop-item">
                    <div class="drop-item-title">${tip.title}</div>
                    <div class="card-content">${tip.content.replace(/\n/g, '<br>')}</div>
                </div>
            `;
        });
    }

    return `
        <div class="card">
            <div class="card-date">${item.date}</div>
            ${itemsHTML}
        </div>
    `;
}

function renderPromptCard(item) {
    let itemsHTML = '';
    if (item.items && Array.isArray(item.items)) {
        item.items.forEach(prompt => {
            const escapedContent = prompt.content.replace(/"/g, '&quot;');
            itemsHTML += `
                <div class="drop-item">
                    <div class="drop-item-title">${prompt.title}</div>
                    <div class="card-content">${prompt.content.replace(/\n/g, '<br>')}</div>
                    <button class="copy-btn" data-prompt="${escapedContent}">Copy Prompt</button>
                </div>
            `;
        });
    }

    return `
        <div class="card">
            <div class="card-date">${item.date}</div>
            ${itemsHTML}
        </div>
    `;
}

function attachCopyListeners(container) {
    const buttons = container.querySelectorAll('.copy-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const promptText = e.target.getAttribute('data-prompt');
            navigator.clipboard.writeText(promptText).then(() => {
                const button = e.target;
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                
                // Revert text after 2 seconds
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            });
        });
    });
}
