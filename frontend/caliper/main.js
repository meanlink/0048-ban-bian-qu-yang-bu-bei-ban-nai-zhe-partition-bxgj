import {mount} from '/base.js'
import {sampling} from './sampling.js'
import {inspection} from './inspection.js'
import {distribution} from './distribution.js'
import {approval} from './approval.js'

const pages={sampling,inspection,distribution,approval}
mount({title:'板边取样簿 · 背板耐折分区',kicker:'样木相框社 / 裁切前材料复测',
  pages:{sampling:'整板取样图',inspection:'夹具检测卡',distribution:'分区挠度图',approval:'边框裁切签发'},
  render:(page,root,user)=>pages[page](root,user)})
