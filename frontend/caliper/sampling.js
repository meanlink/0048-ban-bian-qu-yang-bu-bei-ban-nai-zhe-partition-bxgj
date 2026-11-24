import {api,empty} from '/base.js'
import {endpoint,head,lotPicker,post,read} from './deck.js'
import {diagram} from './board.js'

export async function sampling(root,user,selected){
  const {lots,code}=await read(selected)
  if(!code){root.innerHTML=empty('背板批号尚未登记。');return}
  const items=await api(endpoint+'/lots/'+code+'/samples')
  root.innerHTML=head('整板取样图','同一张板的靠边带和中腹区各留独立样品，领用后可追溯到整板。')
   +`<div class="frame-grid"><section>${diagram(items)}</section><aside>${lotPicker(lots,code)}
   ${user.role==='operator'?`<form><label>取样号<input name="code" required pattern="[A-Z0-9-]{3,24}"></label><label>整板标签<input name="sheet" minlength="2" maxlength="24" required></label>
    <label>样区<select name="zone"><option value="bound">靠边带</option><option value="heart">中腹区</option></select></label>
    <button>登记样片</button><p role="status"></p></form>`:''}</aside></div>`
  root.querySelector('#lot').onchange=e=>sampling(root,user,e.target.value)
  post(root.querySelector('form'),body=>api(endpoint+'/samples','POST',{...body,lot:code}),()=>sampling(root,user,code))
}
