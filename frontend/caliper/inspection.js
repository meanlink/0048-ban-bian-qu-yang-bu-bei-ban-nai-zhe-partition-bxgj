import {api,empty} from '/base.js'
import {endpoint,head,lotPicker,post,read} from './deck.js'
import {fixtureSlip} from './fixture-slip.js'
import {cardTable} from './card-table.js'
import {dialForm} from './dial-form.js'

export async function inspection(root,user,selected){
  const {lots,code}=await read(selected)
  if(!code){root.innerHTML=empty('先登记背板批次。');return}
  const path=endpoint+'/lots/'+code
  const [cards,samples,fixtures]=await Promise.all([api(path+'/cards'),api(path+'/samples'),api(endpoint+'/fixtures')])
  const ready=samples.filter(row=>!row.active_card)
  root.innerHTML=head('夹具检测卡','记录夹具、检测日与原读数。零位校正由后端计算；占位失误的卡需由复核人排除。')
    +`<div class="frame-grid"><section>${cards.length?cardTable(cards,user.role):empty('该批次没有检测卡。')}</section>
    <aside>${lotPicker(lots,code)}${fixtureSlip(fixtures)}${user.role==='operator'&&ready.length?dialForm(ready,fixtures):''}</aside></div>`
  root.querySelector('#lot').onchange=e=>inspection(root,user,e.target.value)
  for(const form of root.querySelectorAll('[data-card]'))
    post(form,body=>api(endpoint+'/cards/'+form.dataset.card+'/exclude','PUT',body),()=>inspection(root,user,code))
  post(root.querySelector('#dial'),body=>api(endpoint+'/cards','POST',{...body,deflection:+body.deflection}),()=>inspection(root,user,code))
}
