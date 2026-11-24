import {h,badge,empty} from '/base.js'

export function diagram(items){
  const locations=[...new Set(items.map(row=>row.sheet))]
  return locations.length?`<section class="boards">${locations.map(id=>{
    const points=items.filter(row=>row.sheet===id)
    return `<article class="board"><h2>${h(id)}</h2><div><span>靠边带</span><span>中腹区</span></div>
    <div>${['bound','heart'].map(zone=>{
      const point=points.find(row=>row.zone===zone)
      return point?`<span><b>${h(point.code)}</b>${badge(point.active_card?'已测':'待测')}</span>`:'<span>无该区取样</span>'
    }).join('')}</div></article>`
  }).join('')}</section>`:empty('该批次尚无裁边与中部取样。')
}
