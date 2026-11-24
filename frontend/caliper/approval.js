import {api,empty} from '/base.js'
import {endpoint,head,lotPicker,post,read} from './deck.js'
import {docket} from './cut-sheet.js'

export async function approval(root,user,selected){
  const {lots,code}=await read(selected)
  if(!code){root.innerHTML=empty('没有待签发背板。');return}
  const path=endpoint+'/lots/'+code
  const {report,order}=await api(path+'/distribution')
  root.innerHTML=head('边框裁切签发','钳具检测通过后给裁切桌签发背板批次和保留内宽，冻结取样与检测。')
    +`<div class="frame-grid"><section>${docket(lots.find(row=>row.code===code),report,order)}</section><aside>${lotPicker(lots,code)}
    ${user.role==='reviewer'&&!order?`<form><label>裁切内宽（mm）<input name="width" type="number" min="10" max="1500" value="220" required></label>
    <button>签发裁切单</button><p role="status"></p></form>`:''}</aside></div>`
  root.querySelector('#lot').onchange=e=>approval(root,user,e.target.value)
  post(root.querySelector('form'),body=>api(path+'/issue','POST',{width:+body.width}),()=>approval(root,user,code))
}
