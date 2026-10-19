// SafeOdds - Interactive Bet Slip Logic
// Plain JavaScript managing in-memory slip selections with smooth UI integration

document.addEventListener('DOMContentLoaded', () => {
    // In-memory list of selected tips
    // Structure: { id, match, tip, odds, confidence }
    let slip = [];

    // DOM Elements
    const slipPanel = document.getElementById('bet-slip');
    const slipTitle = document.getElementById('slip-title');
    const slipClear = document.getElementById('slip-clear');
    const slipClose = document.getElementById('slip-close');
    const slipEmpty = document.getElementById('slip-empty');
    const slipList = document.getElementById('slip-list');
    const slipOdds = document.getElementById('slip-odds');
    const slipChance = document.getElementById('slip-chance');
    const navSlipCount = document.getElementById('navSlipCount');
    const toggleSlipBtn = document.getElementById('toggleSlipBtn');
    const addButtons = document.querySelectorAll('.btn-add-slip');

    // Fire-and-forget analytics beacon (no cookies, no personal data)
    function trackClick(target, matchId) {
        try {
            if (!navigator.sendBeacon) return;
            const data = new FormData();
            data.append('target', target);
            if (matchId) data.append('match_id', matchId);
            navigator.sendBeacon('/api/track/', data);
        } catch (e) { /* ignore */ }
    }

    // Update slip calculations and DOM
    function renderSlip() {
        const count = slip.length;
        if (slipTitle) {
            slipTitle.textContent = `YOUR SLIP — ${count} ${count === 1 ? 'Game' : 'Games'}`;
        }
        if (navSlipCount) {
            navSlipCount.textContent = count;
        }

        if (count === 0) {
            if (slipEmpty) slipEmpty.style.display = 'block';
            if (slipList) slipList.innerHTML = '';
            if (slipOdds) slipOdds.textContent = '1.00';
            if (slipChance) slipChance.textContent = '0%';
        } else {
            if (slipEmpty) slipEmpty.style.display = 'none';

            // Calculate total odds (product of all odds)
            let totalOdds = 1.0;
            // Calculate combined chance: product of (confidence / 100)
            let combinedChance = 1.0;

            if (slipList) {
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
                            <button class="slip-item-remove" data-id="${item.id}" title="Remove item">&times;</button>
                        </div>
                    `;
                    slipList.appendChild(li);
                });
            }

            if (slipOdds) slipOdds.textContent = totalOdds.toFixed(2);
            if (slipChance) slipChance.textContent = `${(combinedChance * 100).toFixed(1)}%`;
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
                btn.textContent = btn.classList.contains('btn-compact-add') ? '+ Slip' : '+ Add to Slip';
            }
        });

        updatePlaceButton();
    }

    // Toggle match in/out of slip
    function toggleSlipItem(matchData) {
        const index = slip.findIndex(item => item.id === matchData.id);
        if (index > -1) {
            slip.splice(index, 1);
        } else {
            slip.push(matchData);
            // Auto expand slip when adding a game
            if (slipPanel) slipPanel.classList.remove('minimized');
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
                confidence: btn.getAttribute('data-confidence'),
                sbIds: btn.getAttribute('data-sb-ids') || ''
            };
            toggleSlipItem(matchData);
            trackClick('add_to_slip', matchData.id);
        });
    });

    // Rebuild the "Place Slip" link so SportyBet receives the current picks
    function updatePlaceButton() {
        const placeBtn = document.getElementById('slip-place-btn');
        if (!placeBtn) return;
        const ids = [];
        slip.forEach(item => {
            (item.sbIds || '').split(',').forEach(raw => {
                const pick = raw.trim();
                if (pick && ids.indexOf(pick) === -1) ids.push(pick);
            });
        });
        placeBtn.setAttribute('href', ids.length ? `/go/sportybet/?ids=${ids.join(',')}` : '/go/sportybet/');
    }

    // Remove single item from slip list
    if (slipList) {
        slipList.addEventListener('click', (e) => {
            if (e.target.classList.contains('slip-item-remove')) {
                const idToRemove = e.target.getAttribute('data-id');
                slip = slip.filter(item => item.id !== idToRemove);
                renderSlip();
            }
        });
    }

    // Clear entire slip
    if (slipClear) {
        slipClear.addEventListener('click', (e) => {
            e.preventDefault();
            slip = [];
            renderSlip();
        });
    }

    // Toggle slip visibility
    if (slipClose && slipPanel) {
        slipClose.addEventListener('click', (e) => {
            e.stopPropagation();
            slipPanel.classList.toggle('minimized');
        });
    }

    if (toggleSlipBtn && slipPanel) {
        toggleSlipBtn.addEventListener('click', () => {
            slipPanel.classList.toggle('minimized');
        });
    }

    // VIP currency toggle ($ / ₦)
    const vipPricing = document.getElementById('vipPricing');
    const vipToggle = document.getElementById('vipCurrencyToggle');
    if (vipPricing && vipToggle) {
        const symbolEl = document.getElementById('vipCurrencySymbol');
        const amountEl = document.getElementById('vipPriceAmount');
        const joinEl = document.getElementById('vipJoinPrice');
        const period = vipPricing.getAttribute('data-period') || '';
        const options = {
            primary: {
                symbol: vipPricing.getAttribute('data-primary-currency') || '',
                price: vipPricing.getAttribute('data-primary-price') || ''
            },
            secondary: {
                symbol: vipPricing.getAttribute('data-secondary-currency') || '',
                price: vipPricing.getAttribute('data-secondary-price') || ''
            }
        };

        const applyCurrency = (target) => {
            const opt = options[target];
            if (!opt) return;
            if (symbolEl) symbolEl.textContent = opt.symbol;
            if (amountEl) amountEl.textContent = opt.price;
            if (joinEl) joinEl.textContent = `${opt.symbol}${opt.price}${period}`;
            vipToggle.querySelectorAll('.vip-currency-opt').forEach((btn) => {
                btn.classList.toggle('is-active', btn.getAttribute('data-target') === target);
            });
            try { localStorage.setItem('vipCurrency', target); } catch (e) { /* ignore */ }
        };

        vipToggle.addEventListener('click', (e) => {
            const btn = e.target.closest('.vip-currency-opt');
            if (btn) applyCurrency(btn.getAttribute('data-target'));
        });

        try {
            const saved = localStorage.getItem('vipCurrency');
            if (saved && options[saved]) applyCurrency(saved);
        } catch (e) { /* ignore */ }
    }

    // Basic XSS protection helper
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Initial render
    renderSlip();
});
