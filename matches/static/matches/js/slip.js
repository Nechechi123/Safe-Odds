// SAFE ODDS - Bet Slip Logic
// Plain JavaScript managing in-memory slip selections

document.addEventListener('DOMContentLoaded', () => {
    // In-memory list of selected tips
    // Structure: { id, match, tip, odds, confidence }
    let slip = [];

    // DOM Elements
    const slipTitle = document.getElementById('slip-title');
    const slipClear = document.getElementById('slip-clear');
    const slipEmpty = document.getElementById('slip-empty');
    const slipList = document.getElementById('slip-list');
    const slipOdds = document.getElementById('slip-odds');
    const slipChance = document.getElementById('slip-chance');
    const addButtons = document.querySelectorAll('.btn-add-slip');

    // Update slip calculations and DOM
    function renderSlip() {
        const count = slip.length;
        slipTitle.textContent = `YOUR SLIP — ${count} ${count === 1 ? 'Game' : 'Games'}`;

        if (count === 0) {
            slipEmpty.style.display = 'block';
            slipList.innerHTML = '';
            slipOdds.textContent = '1.00';
            slipChance.textContent = '0%';
        } else {
            slipEmpty.style.display = 'none';

            // Calculate total odds (product of all odds)
            let totalOdds = 1.0;
            // Calculate combined chance: product of (confidence / 100)
            let combinedChance = 1.0;

            slipList.innerHTML = '';
            slip.forEach(item => {
                totalOdds *= parseFloat(item.odds);
                combinedChance *= (parseFloat(item.confidence) / 100);

                const li = document.createElement('li');
                li.className = 'slip-item';
                li.innerHTML = `
                    <div class="slip-item-info">
                        <span class="slip-item-match">${escapeHtml(item.match)}</span>
                        <span class="slip-item-tip">${escapeHtml(item.tip)}</span>
                    </div>
                    <div style="display:flex; align-items:center;">
                        <span class="slip-item-odds">@${item.odds}</span>
                        <button class="slip-item-remove" data-id="${item.id}" title="Remove">&times;</button>
                    </div>
                `;
                slipList.appendChild(li);
            });

            slipOdds.textContent = totalOdds.toFixed(2);
            slipChance.textContent = `${(combinedChance * 100).toFixed(1)}%`;
        }

        // Update card button states
        addButtons.forEach(btn => {
            const matchId = btn.getAttribute('data-id');
            const isAdded = slip.some(item => item.id === matchId);
            if (isAdded) {
                btn.classList.add('added');
                btn.textContent = '✓ Added';
            } else {
                btn.classList.remove('added');
                btn.textContent = '+ Add to Slip';
            }
        });
    }

    // Toggle match in/out of slip
    function toggleSlipItem(matchData) {
        const index = slip.findIndex(item => item.id === matchData.id);
        if (index > -1) {
            slip.splice(index, 1);
        } else {
            slip.push(matchData);
        }
        renderSlip();
    }

    // Event listener for "Add to Slip" buttons on cards
    addButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const matchData = {
                id: btn.getAttribute('data-id'),
                match: btn.getAttribute('data-match'),
                tip: btn.getAttribute('data-tip'),
                odds: btn.getAttribute('data-odds'),
                confidence: btn.getAttribute('data-confidence')
            };
            toggleSlipItem(matchData);
        });
    });

    // Remove single item from slip list
    slipList.addEventListener('click', (e) => {
        if (e.target.classList.contains('slip-item-remove')) {
            const idToRemove = e.target.getAttribute('data-id');
            slip = slip.filter(item => item.id !== idToRemove);
            renderSlip();
        }
    });

    // Clear entire slip
    if (slipClear) {
        slipClear.addEventListener('click', (e) => {
            e.preventDefault();
            slip = [];
            renderSlip();
        });
    }

    // Basic XSS protection
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Initial render
    renderSlip();
});
