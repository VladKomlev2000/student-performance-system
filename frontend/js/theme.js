(function() {
    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    document.body.appendChild(btn);

    function applyDark() {
        document.documentElement.style.setProperty('--bg', '#1a1a2e');
        document.documentElement.style.setProperty('--card-bg', '#16213e');
        document.documentElement.style.setProperty('--text', '#e0e0e0');
        document.documentElement.style.setProperty('--text-light', '#a0a0a0');
        document.documentElement.style.setProperty('--border', '#2a2a4a');
        document.body.classList.add('dark');
        btn.textContent = '☀️';
    }

    function applyLight() {
        document.documentElement.style.setProperty('--bg', '#f5f6fa');
        document.documentElement.style.setProperty('--card-bg', '#ffffff');
        document.documentElement.style.setProperty('--text', '#2d3436');
        document.documentElement.style.setProperty('--text-light', '#636e72');
        document.documentElement.style.setProperty('--border', '#dfe6e9');
        document.body.classList.remove('dark');
        btn.textContent = '🌙';
    }

    if (localStorage.getItem('theme') === 'dark') {
        applyDark();
    } else {
        applyLight();
    }

    btn.addEventListener('click', function() {
        if (document.body.classList.contains('dark')) {
            applyLight();
            localStorage.setItem('theme', 'light');
        } else {
            applyDark();
            localStorage.setItem('theme', 'dark');
        }
    });
})();