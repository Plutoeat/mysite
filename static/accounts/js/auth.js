window.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const emailInput = document.querySelector('input[name="email"]');
    const codeBtn = document.querySelector('#codeBtn');

    emailInput.addEventListener('input', function () {
        codeBtn.disabled = !emailInput.value
    })

    codeBtn.addEventListener('click', function (event) {
        if (!emailInput.value) {
            event.preventDefault();
            alert('请填写邮箱后再提交！');
        } else {
            getVerifyCode();
            codeBtn.innerHTML = '<span>请于5分钟后再次尝试</span>'
            codeBtn.disabled = true;
            setTimeout(function () {
                codeBtn.innerHTML = '<span>获取验证码</span>'
                codeBtn.disabled = !emailInput.value
            }, 300000)
        }
    })

    function getVerifyCode() {
        const formData = new URLSearchParams({
            email: emailInput.value
        });
        fetch("{% url 'accounts:forget_password_code' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: formData
        }).then(() => {
        });
    }
})