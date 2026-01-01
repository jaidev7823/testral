// shortcut.js
export const INJECT_NUMBERS = () => {
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    const els = document.querySelectorAll(
        "button,a,input,select,textarea,[role='button'],[role='link'],[onclick]"
    );

    let idx = 0;

    els.forEach(el => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);

        if (
            r.width < 3 || r.height < 3 ||
            s.display === 'none' ||
            s.visibility === 'hidden' ||
            s.opacity === '0'
        ) return;

        if (r.bottom < 0 || r.right < 0 || r.top > vh || r.left > vw) return;

        el.setAttribute('data-ai-idx', idx);

        const b = document.createElement('div');
        b.className = 'ai-number-badge';
        b.innerText = idx;
        b.style.cssText = `
            position:fixed;
            left:${Math.max(0, r.left)}px;
            top:${Math.max(0, r.top)}px;
            background:yellow;
            color:black;
            font-size:12px;
            font-weight:bold;
            padding:1px 4px;
            border-radius:3px;
            z-index:2147483647;
            pointer-events:none;
        `;
        document.body.appendChild(b);
        idx++;
    });
};

export const REMOVE_NUMBERS = () => {
    document.querySelectorAll('.ai-number-badge').forEach(e => e.remove());
};
