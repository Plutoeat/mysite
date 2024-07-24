document.addEventListener("DOMContentLoaded", function () {
    // 处理全局 collapse 事件（双纯icon事件）
    // 1. 获取元素
    const navbarCollapseBtns = document.querySelectorAll('button[aria-controls]');

    navbarCollapseBtns.forEach(function (navbarCollapseBtn) {
        navbarCollapseBtn.addEventListener('click', function () {
            const controlIcons = navbarCollapseBtn.querySelectorAll('span');
            const controlId = navbarCollapseBtn.getAttribute('data-x-collapse');
            const controlElement = document.querySelector(controlId);
            const otherControlElement = document.querySelectorAll('.x-collapse.collapse-active');

            // 所有icon样式复原
            navbarCollapseBtns.forEach(navbarCollapseBtn => {
                for (let i = 0; i < navbarCollapseBtn.querySelectorAll('.material-symbols-outlined.x-collapse-icon').length; i++) {
                    if (i === 0) {
                        if (navbarCollapseBtn.querySelectorAll('.material-symbols-outlined.x-collapse-icon')[i].classList.contains('hidden')) {
                            navbarCollapseBtn.querySelectorAll('.material-symbols-outlined.x-collapse-icon')[i].classList.remove('hidden');
                        }
                    }
                    if (i === 1) {
                        if (!navbarCollapseBtn.querySelectorAll('.material-symbols-outlined.x-collapse-icon')[i].classList.contains('hidden')) {
                            navbarCollapseBtn.querySelectorAll('.material-symbols-outlined.x-collapse-icon')[i].classList.add('hidden');
                        }
                    }
                }
            });

            // 处于活跃状态的收起内容收起
            otherControlElement.forEach(function (content) {
                if (content !== controlElement) {
                    content.classList.remove('collapse-active');
                }
            });

            // icon 切换
            controlIcons.forEach(controlIcon => {
                if (controlIcon.classList.contains('material-symbols-outlined') && controlIcon.classList.contains('x-collapse-icon')) {
                    controlIcon.classList.toggle('hidden');
                }
            });

            // 收起内容切换活跃状态
            controlElement.classList.toggle('collapse-active');
        }.bind(this));
    });
});

window.onload = function () {
    initTheme();
};

// 初始化主题
function initTheme() {
    // 1. 获取元素
    const lightModeIcons = document.querySelectorAll('span[aria-label="light-mode"]');
    const darkModeIcons = document.querySelectorAll('span[aria-label="dark-mode"]');

    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        lightModeIcons.forEach(lightModeIcon => {
            lightModeIcon.classList.remove('hidden');
        })
        darkModeIcons.forEach(darkModeIcon => {
            darkModeIcon.classList.add('hidden');
        })
    } else {
        document.documentElement.classList.remove('dark');
        lightModeIcons.forEach(lightModeIcon => {
            lightModeIcon.classList.add('hidden');
        })
        darkModeIcons.forEach(darkModeIcon => {
            darkModeIcon.classList.remove('hidden');
        })
    }
    // Whenever the user explicitly chooses light mode
    // localStorage.theme = 'light'

    // Whenever the user explicitly chooses dark mode
    // localStorage.theme = 'dark'

    // Whenever the user explicitly chooses to respect the OS preference
    // localStorage.removeItem('theme')
}

// 主题切换
function selectTheme() {
    if (localStorage.theme === 'light') {
        localStorage.theme = 'dark';
    } else if(localStorage.theme === 'dark') {
        localStorage.theme = 'light';
    } else {
        localStorage.theme = 'light';
    }
    initTheme();
}