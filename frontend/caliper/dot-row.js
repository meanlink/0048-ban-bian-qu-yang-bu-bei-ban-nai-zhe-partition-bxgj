import {h} from '/base.js'
import {mm,zones} from './lexicon.js'

export function dotRow(key,row,limit,axis){
  const proportion=value=>100*value/axis
  return `<article class="plot-row"><h2>${zones[key]}</h2><div class="dot-axis" aria-label="挠度分布（毫米）">
    <span class="limit" style="left:${proportion(limit)}%" title="P90 上限 ${mm(limit)}"></span>
    ${row.values.map((value,index)=>`<span class="point" style="left:${proportion(value)}%;top:${15+(index%3)*12}px" title="${mm(value)}"></span>`).join('')}</div>
    <p><span>样本 ${row.n}</span><span>中位数 ${h(mm(row.median))}</span>
    <span>P90 ${h(mm(row.p90))}</span><span>MAD ${h(mm(row.mad))}</span></p></article>`
}
