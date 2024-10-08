document.addEventListener("DOMContentLoaded", function () {
    const tocButton = document.getElementById('tocButton');
    const tocDrawer = document.getElementById('tocDrawer');

    tocButton.addEventListener('click', () => {
        tocDrawer.classList.toggle('hidden');
    });

    tocDrawer.addEventListener('click', () => {
        tocDrawer.classList.add('hidden');
    });

    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ]
    })

    function redirectPageCenter(anchor) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const target = document.querySelector(this.getAttribute('href'));
            const offset = window.innerHeight / 2 - target.getBoundingClientRect().height / 2;
            if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                target.setAttribute('style', 'background-color: #312e81');
            } else {
                target.setAttribute('style', 'background-color: #e0e7ff');
            }

            setTimeout(function () {
                target.removeAttribute('style')
            },3000)

            window.scroll({
                top: target.offsetTop - offset,
                behavior: 'smooth'
            });
        });
    }

    document.querySelectorAll('a[href^="#"]:not(.footnote-backref):not(.footnote-ref)').forEach(anchor => {
        redirectPageCenter(anchor);
    });

    document.querySelectorAll('a[href^="#fn"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            const offset = window.innerHeight / 2 - target.getBoundingClientRect().height / 2;
            if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                target.setAttribute('style', 'background-color: #312e81');
            } else {
                target.setAttribute('style', 'background-color: #e0e7ff');
            }

            setTimeout(function () {
                target.removeAttribute('style')
            },3000)

            window.scroll({
                top: target.offsetTop - offset,
                behavior: 'smooth'
            });
        });
    });

})