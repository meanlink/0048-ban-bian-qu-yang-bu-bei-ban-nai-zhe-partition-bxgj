import {opts} from './deck.js'

export function dialForm(samples,fixtures) {
  return `<form id="dial"><label>样片<select name="sample">${opts(samples,'code',r=>r.code+' / '+r.sheet)}</select></label>
    <label>夹具<select name="fixture">${opts(fixtures,'code',r=>r.label)}</select></label>
    <label>检测日期<input name="observed_on" type="date" required value="2026-11-19"></label>
    <label>实读最大挠度（mm）<input name="deflection" type="number" min="0" max="99" step=".01" required></label>
    <button>记录检测卡</button><p role="status"></p></form>`
}
