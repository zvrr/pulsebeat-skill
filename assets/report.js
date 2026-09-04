'use strict';
document.getElementById('print').addEventListener('click',()=>window.print());
document.getElementById('chart-window').addEventListener('change',event=>{document.querySelectorAll('[data-window]').forEach(panel=>{panel.hidden=panel.dataset.window!==event.target.value;});});

const providerPicker=document.getElementById('music-provider');
if(providerPicker)providerPicker.addEventListener('change',()=>document.querySelectorAll('[data-music-provider]').forEach(panel=>{panel.hidden=panel.dataset.musicProvider!==providerPicker.value;}));
