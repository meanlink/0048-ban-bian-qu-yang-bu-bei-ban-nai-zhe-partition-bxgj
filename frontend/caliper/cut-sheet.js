import {h,badge} from '/base.js'
import {decision,mm,zones,orderStatus} from './lexicon.js'

export function docket(lot,report,order){
  return `<article class="docket"><div class="cut-header"><h2>${h(lot.label)}</h2>${badge(decision[report.status],report.status)}</div>
    <p>当前厚度 ${mm(lot.panel_mm)} · 批号 ${h(lot.code)}</p>
    <dl>${Object.entries(report.zones).map(([zone,row])=>`<div><dt>${zones[zone]}</dt><dd>P90 ${mm(row.p90)}<br>MAD ${mm(row.mad)}</dd></div>`).join('')}</dl>
    ${order?`<p>当前裁切单 #${order.id} · 边框内宽 ${mm(order.kept_width)} · 签发员 ${h(order.issuer)} · ${badge(orderStatus[order.status],order.status)}</p>`:''}</article>`
}

export function orderHistory(orders){
  if(!orders?.length)return ''
  return `<section class="docket history"><h2>裁切单留档</h2><div class="card-table"><table>
    <thead><tr><th>单号</th><th>内宽</th><th>状态 / 凭据</th><th>签发与停用</th></tr></thead><tbody>
    ${orders.map(row=>`<tr><th scope="row">#${row.id}</th><td>${mm(row.kept_width)}</td>
      <td>${badge(orderStatus[row.status],row.status)}<small>批签凭据：${h(row.job_status)}${row.job_error?` · ${h(row.job_error)}`:''}</small></td>
      <td>${h(row.issuer)} · ${h(String(row.created_at))}<small>${row.status==='voided'?`${h(row.voided_by)} 停用：${h(row.void_reason)}`:'检测快照已随单留档'}</small></td></tr>`).join('')}
    </tbody></table></div></section>`
}
