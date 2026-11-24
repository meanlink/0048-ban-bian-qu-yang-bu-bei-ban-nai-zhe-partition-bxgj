import {h} from '/base.js'
import {mm} from './lexicon.js'

export const fixtureSlip=fixtures=>`<div class="jigs">${fixtures.map(jig=>`<p><strong>${h(jig.label)}</strong><small>
   适配 ${mm(jig.panel_mm)} / 跨距 ${mm(jig.span_mm)} / 有效期 ${h(jig.cal_due)} / 零位 ${mm(jig.offset_mm)}</small></p>`).join('')}</div>`
