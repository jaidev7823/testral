# shortcut.py

INJECT_NUMBERS = """
() => {
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    const els = document.querySelectorAll(
        "button, a, input, select, textarea, svg, span, div, i, [role='button'], [onclick]"
    );

    let idx = 0;

    els.forEach(el => {
        try {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);

            // visibility filter
            if (
                r.width < 3 || r.height < 3 ||
                s.display === 'none' ||
                s.visibility === 'hidden' ||
                s.opacity === '0'
            ) return;

            // viewport filter
            if (
                r.bottom < 0 ||
                r.right < 0 ||
                r.top > vh ||
                r.left > vw
            ) return;

            // 🔑 CLICKABILITY LOGIC (THIS IS THE FIX)
            const clickable =
                ['BUTTON','A','INPUT','SELECT','TEXTAREA'].includes(el.tagName) ||
                el.hasAttribute('onclick') ||
                el.getAttribute('role') === 'button' ||
                s.cursor === 'pointer' ||
                el.closest('[role="dialog"], .modal, .popup');

            if (!clickable) return;

            el.setAttribute('data-ai-idx', idx);

            const b = document.createElement('div');
            b.className = 'ai-number-badge';
            b.innerText = idx;
            b.style.position = 'fixed';
            b.style.left = Math.max(0, r.left) + 'px';
            b.style.top = Math.max(0, r.top) + 'px';
            b.style.background = 'yellow';
            b.style.color = 'black';
            b.style.fontSize = '12px';
            b.style.fontWeight = 'bold';
            b.style.padding = '1px 4px';
            b.style.borderRadius = '3px';
            b.style.zIndex = '2147483647';
            b.style.pointerEvents = 'none';

            document.body.appendChild(b);
            idx++;
        } catch {}
    });
}
"""


REMOVE_NUMBERS = """
() => {
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());
}
"""
