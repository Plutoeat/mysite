document.addEventListener("DOMContentLoaded",function(){const tocButton=document.getElementById('tocButton');const tocDrawer=document.getElementById('tocDrawer');tocButton.addEventListener('click',()=>{tocDrawer.classList.toggle('hidden');});tocDrawer.addEventListener('click',()=>{tocDrawer.classList.add('hidden');});document.querySelectorAll('a[href^="#"]').forEach(anchor=>{anchor.addEventListener('click',function(e){e.preventDefault();const target=document.querySelector(this.getAttribute('href'));const offset=window.innerHeight/2-target.getBoundingClientRect().height/2;target.classList.add('bg-indigo-800/65');target.classList.add('dark:bg-indigo-200/65');setTimeout(function(){target.classList.remove('bg-indigo-800/65');target.classList.remove('dark:bg-indigo-200/65');},2000)
window.scroll({top:target.offsetTop-offset,behavior:'smooth'});});});});