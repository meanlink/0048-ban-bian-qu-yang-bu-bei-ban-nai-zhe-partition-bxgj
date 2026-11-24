import {h,badge} from '/base.js'
import {decision,mm,zones} from './lexicon.js'

export function docket(lot,report,order){
  return `<article class="docket"><div class="cut-header"><h2>${h(lot.label)}</h2>${badge(decision[report.status],report.status)}</div>
    <p>当前厚度 ${mm(lot.panel_mm)} · 批号 ${h(lot.code)}</p>
    <dl>${Object.entries(report.zones).map(([zone,row])=>`<div><dt>${zones[zone]}</dt><dd>P90 ${mm(row.p90)}<br>MAD ${mm(row.mad)}</dd></div>`).join('')}</dl>
    ${order?`<p>已签发边框内宽 ${mm(order.kept_width)} · 签发员 ${h(order.issuer)}</p>`:''}</article>`
}
