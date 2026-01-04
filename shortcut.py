# shortcut.py

INJECT_NUMBERS = """
() => {
    // 1. Cleanup
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());

    const vh = window.innerHeight;
    const vw = window.innerWidth;

    // 2. Identify the Active Overlay (Market standard for "top layer")
    // We target the most likely popup containers first
    const activeOverlay = document.querySelector('[role="dialog"], .modal, .popup, .overlay, [aria-modal="true"]');

    // 3. Selection Strategy: Focus only on high-intent elements
    // If an overlay exists, we ONLY look inside it. If not, we look at the body.
    const root = activeOverlay || document.body;
    const selectors = 'button, input, select, textarea, [role="button"], [onclick], .close, [aria-label*="close" i]';
    const elements = Array.from(root.querySelectorAll(selectors));

    let idx = 0;

    elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);

        // Logic Filter: Ignore hidden, tiny, or off-screen elements
        if (
            rect.width < 5 || rect.height < 5 ||
            style.display === 'none' ||
            style.visibility === 'hidden' ||
            style.opacity === '0' ||
            rect.bottom < 0 || rect.top > vh ||
            rect.right < 0 || rect.left > vw
        ) return;

        // Surgical Check: Is it actually clickable?
        if (style.pointerEvents === 'none') return;

        // 4. Enhanced UI/UX for the Badge
        const badge = document.createElement('div');
        badge.className = 'ai-number-badge';
        badge.innerText = idx;
        
        // Data attribute for the AI to reference later
        el.setAttribute('data-ai-idx', idx);

        Object.assign(badge.style, {
            position: 'fixed',
            left: `${rect.left}px`,
            top: `${rect.top}px`,
            zIndex: '2147483647',
            pointerEvents: 'none',
            // Professional Look: Contrast, Shadow, and Font
            background: '#000000',
            color: '#ffffff',
            border: '1px solid #ffffff',
            padding: '2px 6px',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: '800',
            fontFamily: 'Inter, system-ui, sans-serif',
            boxShadow: '0px 2px 4px rgba(0,0,0,0.5)',
            transform: 'translate(-50%, -50%)', // Center on the top-left corner
            lineHeight: '1'
        });

        document.body.appendChild(badge);
        idx++;
    });
}
"""


REMOVE_NUMBERS = """
() => {
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());
}
"""
