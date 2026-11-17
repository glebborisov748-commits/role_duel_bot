"""Generated portrait presets with local appearance controls and clothed fitting previews."""
import base64
from functools import lru_cache
from pathlib import Path
import character_options as options
import profile_options

HAIR={'brown':'#684039','black':'#23222e','blonde':'#e9c887','red':'#b65b39','silver':'#e3e2ec','pink':'#e5a1be','purple':'#b799d7','blue':'#4c628d'}
SKIN={'fair':'#f7dfd2','light':'#e9c7b2','olive':'#c4ab83','tan':'#bc8d6d','brown':'#956347','dark':'#654333'}
EYES={'brown':'#765644','blue':'#72adcd','green':'#83ad87','grey':'#9ca7b2','amber':'#c7a35f','violet':'#ac8dcd'}

def rgb(color):return [int(color[i:i+2],16)/255 for i in (1,3,5)]

@lru_cache(maxsize=64)
def base(world,gender,style):
 path=Path(__file__).resolve().parent/'assets'/('avatar_'+world+'_'+gender+'_'+style+'.webp')
 if not path.is_file():path=path.parent/('portrait_'+gender+'.webp')
 return base64.b64encode(path.read_bytes()).decode()

def svg(raw,gender='female'):
 o=options.validate(raw,gender);male=gender=='male';gender='male' if male else 'female'
 race=raw.get('race') or {'cat':'catfolk','elf':'elf'}.get(raw.get('species'),'human')
 world='realism' if raw.get('world')=='realism' else 'anime'
 eye_y=({'long':108,'waves':108,'bob':110,'short':109,'curls':111,'ponytail':112,'braid':108,'pixie':112}[o['hair_style']] if world=='anime' else {'long':115,'waves':115,'bob':118,'short':118,'curls':118,'ponytail':119,'braid':119,'pixie':120}[o['hair_style']]) if not male else ({'sidepart':121,'slicked':121,'curls_short':122,'medium':122}.get(o['hair_style'],125) if world=='realism' else 124)
 src='data:image/webp;base64,'+base(world,gender,o['hair_style']);color=rgb(HAIR[o['hair_color']]);skin=rgb(SKIN[o['skin']]);eye=EYES[o['eyes']];iris=rgb(eye)
 hair_transfer=''.join(f'<feFunc{channel} type="linear" slope="{.3 if o["hair_color"]=="black" else .65}" intercept="{value*(.3 if o["hair_color"]=="black" else .6)}"/>' for channel,value in zip('RGB',color))
 eye_transfer=''.join(f'<feFunc{channel} type="linear" slope=".6" intercept="{value*.45}"/>' for channel,value in zip('RGB',iris))
 skin_transfer=''.join(f'<feFunc{channel} type="linear" slope="{min(1.25,value/baseline)}"/>' for channel,value,baseline in zip('RGB',skin,(.87,.66,.53)))
 defs=f'<defs><filter color-interpolation-filters="sRGB" id="hair-dye"><feColorMatrix type="saturate" values="0"/><feComponentTransfer>{hair_transfer}</feComponentTransfer></filter><filter color-interpolation-filters="sRGB" id="hair-isolation"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 8.4 8.4 -27.6 0 0"/></filter><filter color-interpolation-filters="sRGB" id="skin-tone"><feComponentTransfer>{skin_transfer}</feComponentTransfer></filter><clipPath id="hair-area"><path d="M0 0H260V300H0Z"/></clipPath><mask id="not-eyes" maskUnits="userSpaceOnUse" x="0" y="0" width="260" height="300"><rect width="260" height="300" fill="white"/><ellipse cx="130" cy="184" rx="52" ry="53" fill="black"/><rect x="99" y="219" width="66" height="62" fill="black"/><ellipse cx="106" cy="{eye_y}" rx="17" ry="11" fill="black"/><ellipse cx="162" cy="{eye_y}" rx="17" ry="11" fill="black"/></mask><clipPath id="eye-region"><ellipse cx="106" cy="{eye_y}" rx="15" ry="6"/><ellipse cx="162" cy="{eye_y}" rx="15" ry="6"/></clipPath><mask id="eye-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="260" height="300"><image width="260" height="300" href="{src}" filter="url(#hair-isolation)" clip-path="url(#eye-region)"/></mask><filter color-interpolation-filters="sRGB" id="eye-dye"><feColorMatrix type="saturate" values="0"/><feComponentTransfer>{eye_transfer}</feComponentTransfer></filter><mask id="hair-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="260" height="300"><image width="260" height="300" href="{src}" filter="url(#hair-isolation)" clip-path="url(#hair-area)" mask="url(#not-eyes)"/></mask><filter color-interpolation-filters="sRGB" id="skin-isolation"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 -3 -3 10 0 0"/></filter><clipPath id="skin-area"><path d="M84 90Q130 72 177 90L181 176L157 210L163 239Q130 262 96 239L103 210L79 174Z"/></clipPath><mask id="skin-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="260" height="300"><image width="260" height="300" href="{src}" filter="url(#skin-isolation)" clip-path="url(#skin-area)"/></mask><linearGradient id="cloth" x2=".8" y2="1"><stop stop-color="#6b5a7b"/><stop offset="1" stop-color="#302b42"/></linearGradient><linearGradient id="ear"><stop stop-color="#e1bca5"/><stop offset="1" stop-color="#b48780"/></linearGradient></defs>'
 portrait=f'<image width="260" height="300" href="{src}"/>'
 if o['hair_color']!='brown':portrait+=f'<image width="260" height="300" href="{src}" filter="url(#hair-dye)" mask="url(#hair-mask)"/>'
 if o['skin']!='light':portrait+=f'<image width="260" height="300" href="{src}" filter="url(#skin-tone)" mask="url(#skin-mask)" opacity=".95"/>'
 if o['eyes']!='brown':portrait+=f'<image width="260" height="300" href="{src}" filter="url(#eye-dye)" mask="url(#eye-mask)"/>'
 extra=''
 if race=='elf':extra+='<path d="M78 135Q64 117 47 116Q52 151 80 158M181 136Q198 117 213 116Q207 152 180 158" fill="url(#ear)"/>'
 if race in ('catfolk','foxfolk','wolffolk'):extra+='<path d="M73 62Q51 37 65 14Q94 20 103 43M159 43Q167 19 196 14Q209 38 188 62" fill="#8d736e"/><path d="M77 44L70 25L93 40M171 40L191 25L184 46" fill="#c5909e"/>'
 if race in ('succubus','dragonborn'):extra+='<path d="M84 52Q46 37 65 9Q64 33 98 36M163 36Q198 30 193 8Q215 37 177 53" fill="#796779" stroke="#c6a9b5" stroke-width="2"/>'
 if race=='angel':extra+='<ellipse cx="130" cy="14" rx="46" ry="7" fill="none" stroke="#e2c48a" stroke-width="4"/>'
 if race=='android':extra+='<path d="M77 127V161L91 174M182 127V161L169 174" fill="none" stroke="#b4c1c1" stroke-width="3"/>'
 if race=='vampire':extra+='<path d="M115 181L118 189L121 181M140 181L143 189L146 181" fill="#eee5df"/>'
 a=o['accessory']
 if a in ('glasses','sunglasses'):extra+='<g fill="'+('#252333' if a=='sunglasses' else 'none')+'" stroke="#c3afce" stroke-width="2.6"><rect x="81" y="112" width="42" height="24" rx="9"/><rect x="138" y="112" width="42" height="24" rx="9"/><path d="M122 121Q130 117 139 121"/></g>'
 if a in ('earrings','stud'):extra+='<circle cx="78" cy="166" r="3" fill="#e2c28c"/>'+('<circle cx="181" cy="166" r="3" fill="#e2c28c"/>' if a=='earrings' else '')
 if a in ('necklace','chain'):extra+='<path d="M97 238Q130 276 163 238" fill="none" stroke="#d6c499" stroke-width="3"/>'
 if a=='scarf':extra+='<path d="M87 233Q130 253 174 233L174 259Q130 280 85 259Z" fill="#ad94ad"/>'
 if a in ('hairclip','ribbon','headband'):extra+='<path d="M171 64L190 74M168 70L187 80" stroke="#d7a1bd" stroke-width="5" stroke-linecap="round"/>'
 extra=extra.replace('y="112"','y="'+str(eye_y-12)+'"').replace('M122 121Q130 117 139 121','M122 '+str(eye_y-3)+'Q130 '+str(eye_y-7)+' 139 '+str(eye_y-3))
 portrait+=extra
 if raw.get('full')!='1':return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 300">'+defs+portrait+'</svg>'
 outfit=raw.get('outfit','');shoulder=39 if male else 52
 body=f'<path d="M{shoulder} 232Q130 201 {260-shoulder} 232L225 391L202 396L188 301L178 428L162 615L139 615L130 437L121 615L98 615L81 428L73 301L59 396L35 391Z" fill="url(#cloth)"/>'
 body+='<path d="M96 610L122 610L122 633L79 633Q77 619 96 610M139 610L163 610L183 629Q187 635 139 633Z" fill="#272531"/>'
 if outfit=='dress':body+='<path d="M77 228Q130 253 182 228L168 340L211 539Q130 566 48 539L92 340Z" fill="#906680"/><path d="M92 340H168" stroke="#d8b5c4" stroke-width="5"/>'
 if outfit=='stockings':body+='<path d="M80 390H127L121 615H98ZM134 390H180L162 615H139Z" fill="#272531"/><path d="M82 397H126M135 397H177" stroke="#bb99b3" stroke-width="6"/><path d="M85 295L175 295L197 405Q130 424 64 405Z" fill="#85718e"/>'
 if outfit=='bunny_outfit':body+='<path d="M77 226L130 250L182 226L173 371L86 371Z" fill="#262632"/><path d="M110 236L130 250L151 235L139 286H121Z" fill="#e8dce4"/><path d="M129 254L113 246L114 267L130 257L147 246L147 267Z" fill="#cf88aa"/>'
 if outfit=='latex_bodysuit':body+='<path d="M75 251L85 395L102 610M181 251L174 395L159 610" stroke="#b9b1c0" stroke-width="5" opacity=".6" fill="none"/>'
 if outfit=='heels':body+='<path d="M97 610L122 610L122 638L114 638L112 626L79 632L80 621ZM139 610L162 610L183 624L181 632L149 626L147 638L139 638Z" fill="#b5809b"/>'
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 650">'+defs+'<rect width="260" height="650" rx="28" fill="#232132"/>'+body+'<g transform="translate(26 0) scale(.8)">'+portrait+'</g></svg>'
