window.addEventListener('DOMContentLoaded',function(){const csrfToken=document.querySelector('input[name="csrfmiddlewaretoken"]').value;const btn=document.querySelector('#logout');function logout(url){fetch(url,{method:"POST",headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRFToken':csrfToken}}).then(()=>{});}});