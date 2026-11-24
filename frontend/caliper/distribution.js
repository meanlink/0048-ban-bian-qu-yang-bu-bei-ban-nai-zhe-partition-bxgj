import {api,empty,badge} from '/base.js'
import {endpoint,head,lotPicker,read} from './deck.js'
import {decision,mm} from './lexicon.js'
import {dotRow} from './dot-row.js'

export async function distribution(root,user,selected){
  const {lots,code}=await read(selected)
  if(!code){root.innerHTML=empty('没有背板可分析。');return}
  const {report}=await api(endpoint+'/lots/'+code+'/distribution')
  const axis=Math.ceil(Math.max(report.p90_limit,...Object.values(report.zones).flatMap(row=>row.values)))+.5
  root.innerHTML=head('分区挠度图','每个点是一张有效检测卡的校正结果。靠边带与中腹区分别计算稳健统计。')
    +`<div class="frame-grid"><section class="stretch">${Object.entries(report.zones).map(([zone,row])=>dotRow(zone,row,report.p90_limit,axis)).join('')}</section>
    <aside>${lotPicker(lots,code)}<h2>签发条件</h2>${badge(decision[report.status],report.status)}
    <p>P90 ≤ ${mm(report.p90_limit)}；MAD ≤ ${mm(report.mad_limit)}。两个区各至少三片。</p></aside></div>`
  root.querySelector('#lot').onchange=e=>distribution(root,user,e.target.value)
}
