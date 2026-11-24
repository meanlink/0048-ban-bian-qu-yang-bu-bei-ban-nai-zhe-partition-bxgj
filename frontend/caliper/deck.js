import {api,h,notice} from '/base.js'

export const head=(title,desc)=>`<header class="frame-head"><h1>${h(title)}</h1><p>${h(desc)}</p></header>`
export const opts=(rows,key,label,value)=>rows.map(row=>`<option value="${h(row[key])}" ${row[key]===value?'selected':''}>${h(label(row))}</option>`).join('')
export const lotPicker=(rows,code)=>`<label>背板批号<select id="lot">${opts(rows,'code',r=>r.label,code)}</select></label>`
export const endpoint='/api/frame'
export async function read(code){
  const lots=await api(endpoint+'/lots')
  return {lots,code:code??lots[0]?.code}
}

export function post(form,action,repaint){
  if(!form)return
  form.onsubmit=async event=>{
    event.preventDefault()
    const button=event.submitter
    button.disabled=true
    try{await action(Object.fromEntries(new FormData(form)));await repaint()}
    catch(error){notice(form.querySelector('[role=status]'),error.message,true)}
    finally{button.disabled=false}
  }
}
