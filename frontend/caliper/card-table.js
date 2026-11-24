import {h,badge} from '/base.js'
import {mm,zones,stages} from './lexicon.js'

export function cardTable(cards,role) {
  return `<div class="card-table"><table><thead><tr><th>样片</th><th>夹具 / 日期</th><th>读数</th><th>零位校正</th><th>证据状态</th></tr></thead><tbody>
    ${cards.map(card=>`<tr><th scope="row">${h(card.sample)}<small>${zones[card.zone]}</small></th>
     <td>${h(card.fixture)}<small>${h(card.observed_on)}</small></td><td>${mm(card.deflection)}</td><td>${mm(card.normalized)}</td>
     <td>${badge(stages[card.stage],card.stage)}${card.exclusion?` <small>${h(card.exclusion)}</small>`:''}
      ${role==='reviewer'&&card.stage==='active'?`<details><summary>排除原卡</summary><form data-card="${card.id}"><label>排除依据<input name="note" minlength="5" maxlength="240" required></label><button>保存</button><p role="status"></p></form></details>`:''}</td></tr>`).join('')}
    </tbody></table></div>`
}
