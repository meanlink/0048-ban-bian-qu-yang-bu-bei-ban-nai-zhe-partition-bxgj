import {api,empty} from '/base.js'
import {endpoint,head,lotPicker,post,read} from './deck.js'
import {docket,orderHistory} from './cut-sheet.js'

const requestKey=()=>crypto.randomUUID().replace(/-/g,'')

export async function approval(root,user,selected){
  const {lots,code}=await read(selected)
  if(!code){root.innerHTML=empty('没有待签发背板。');return}
  const path=endpoint+'/lots/'+code
  const data=await api(path+'/distribution')
  let {report,order,orders}=data
  let token=data.preview_token
  const lot=lots.find(row=>row.code===code)
  const reviewer=user.role==='reviewer'
  root.innerHTML=head('边框裁切签发','钳具检测通过后给裁切桌签发背板批次和保留内宽。样片夹偏时可停用旧裁切单并写明原因，批次复测达标后换发；停用后旧批签凭据不再下发。')
    +`<div class="frame-grid"><section>${docket(lot,report,order)}${orderHistory(orders)}</section>
    <aside>${lotPicker(lots,code)}
    ${order&&reviewer?`<form data-void><h2>停用旧裁切单</h2>
      <label>停用原因（将随单留档）<textarea name="reason" minlength="5" maxlength="240" required placeholder="如：样片压线偏移，原检测卡排除后复测"></textarea></label>
      <button type="submit">停用并开放复测</button><p role="status"></p></form>`:''}
    ${!order&&reviewer?`<form data-issue><h2>${orders.length?'复测后换发':'签发裁切单'}</h2>
      <label>裁切内宽（mm）<input name="width" type="number" min="10" max="1500" value="220" required></label>
      <button type="submit">${orders.length?'换发新裁切单':'签发裁切单'}</button><p role="status"></p></form>`:''}
    ${order?'<p class="muted">批次处于有效裁切单冻结状态；停用后才能对原批次复测。</p>':''}</aside></div>`
  root.querySelector('#lot').onchange=e=>approval(root,user,e.target.value)
  const issueForm=root.querySelector('[data-issue]')
  if(issueForm)post(issueForm,async body=>{
    try{
      return await api(path+'/issue','POST',{width:+body.width,request_key:requestKey(),preview_token:token})
    }catch(error){
      // The preview aged out (inspection changed first); refresh the token so
      // the reviewer can retry immediately without losing the entered width.
      if(error.status===409){const fresh=await api(path+'/distribution');token=fresh.preview_token}
      throw error
    }
  },()=>approval(root,user,code))
  const voidForm=root.querySelector('[data-void]')
  if(voidForm)post(voidForm,body=>api(path+'/void','POST',{reason:body.reason}),()=>approval(root,user,code))
}
