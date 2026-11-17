"""Deterministic vector appearance preview. No provider calls, personal text or external URLs."""
import character_options as options

HAIR={'brown':'#684039','black':'#23222e','blonde':'#e9c887','red':'#b65b39','silver':'#e3e2ec','pink':'#e5a1be','purple':'#b799d7','blue':'#4c628d'}
SKIN={'fair':'#f7dfd2','light':'#e9c7b2','olive':'#c4ab83','tan':'#bc8d6d','brown':'#956347','dark':'#654333'}
EYES={'brown':'#765644','blue':'#72adcd','green':'#83ad87','grey':'#9ca7b2','amber':'#c7a35f','violet':'#ac8dcd'}

def svg(raw,gender='female'):
 o=options.validate(raw);h=HAIR[o['hair_color']];skin=SKIN[o['skin']];eye=EYES[o['eyes']];style=o['hair_style'];male=gender=='male'
 long=style in ('long','waves','curls','braid','ponytail')
 back=f'<path d="M65 156Q49 49 129 41Q211 39 194 164L204 250Q179 263 161 237L96 241Q66 263 52 244Z" fill="{h}"/>' if long else f'<path d="M70 146Q49 38 132 39Q208 41 187 151Z" fill="{h}"/>'
 if style=='ponytail':back=f'<path d="M179 80Q242 107 207 240L180 218Q203 160 172 132Z" fill="{h}"/>'+back
 if style=='braid':back+=''.join(f'<ellipse cx="182" cy="{y}" rx="16" ry="13" fill="{h}" stroke="#000" stroke-opacity=".12"/>' for y in range(150,246,17))
 if style=='curls':back+=''.join(f'<circle cx="{x}" cy="{y}" r="18" fill="{h}"/>' for x in (65,191) for y in range(94,229,28))
 front={
 'long':'M70 110Q62 48 132 46Q200 46 190 115Q157 84 127 72Q101 97 70 110Z',
 'waves':'M67 119Q49 63 104 47Q176 20 192 90L191 126Q169 105 157 78Q129 104 101 104L87 158L68 177Z',
 'bob':'M66 162L64 92Q65 44 131 43Q196 45 195 97L196 174L176 162L174 91Q133 113 82 93L85 165Z',
 'short':'M67 114L62 84L76 72L72 55L101 53L120 36L145 46L168 41L188 65L199 93L186 117L171 84L95 88L76 115Z',
 'curls':'M66 112Q50 67 84 60Q79 37 110 44Q132 23 149 43Q187 33 187 63Q214 77 189 119L171 86L91 86Z',
 'ponytail':'M67 118Q57 42 132 43Q202 48 190 119L174 90Q135 108 85 86L79 120Z',
 'braid':'M66 118Q56 44 132 43Q203 48 190 119L172 85L137 66L89 90L80 120Z',
 'pixie':'M67 115Q51 68 85 51Q137 24 175 53Q199 71 191 112L166 88L175 72L145 89L115 73L91 101L76 123Z',
 }[style]
 jaw='M80 100Q78 151 98 178L128 195L159 180Q181 158 180 100Z' if male else 'M79 100Q78 157 100 179Q129 203 157 179Q181 154 180 100Z'
 ears=''
 if o['species']=='cat':ears=f'<path d="M71 77L63 15L111 51M151 49L198 15L187 82" fill="{h}" stroke="{h}" stroke-width="9" stroke-linejoin="round"/><path d="M75 58L71 31L94 51M168 51L189 31L183 61" fill="#cf8b9d"/>'
 elif o['species']=='elf':ears=f'<path d="M83 118L48 96Q57 145 85 146M178 118L212 96Q204 145 176 146" fill="{skin}"/>'
 accessories=''
 if o['accessory']=='glasses':accessories='<g fill="none" stroke="#c5b6d5" stroke-width="3"><rect x="81" y="117" width="40" height="27" rx="12"/><rect x="140" y="117" width="40" height="27" rx="12"/><path d="M121 126Q130 120 140 126"/></g>'
 elif o['accessory']=='earrings':accessories='<g fill="#e4c482"><circle cx="78" cy="151" r="5"/><circle cx="181" cy="151" r="5"/></g>'
 elif o['accessory']=='necklace':accessories='<path d="M102 216Q130 254 158 216" fill="none" stroke="#dfc38a" stroke-width="2"/><path d="M130 235L136 243L130 251L124 243Z" fill="#e6b4dc"/>'
 elif o['accessory']=='hairclip':accessories='<path d="M166 79L187 86M163 85L184 92" stroke="#e1bedc" stroke-width="5" stroke-linecap="round"/>'
 return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 300" role="img" aria-label="Appearance preview"><defs><radialGradient id="bg"><stop stop-color="#393047"/><stop offset="1" stop-color="#191b2c"/></radialGradient><linearGradient id="shirt" x2="0" y2="1"><stop stop-color="#7f718f"/><stop offset="1" stop-color="#403b56"/></linearGradient></defs><rect width="260" height="300" rx="32" fill="url(#bg)"/>{back}<path d="M35 300L43 252Q48 227 101 215L105 171L154 171L158 215Q212 228 218 252L225 300Z" fill="{skin}"/><path d="M35 300L43 252Q49 229 100 215Q130 239 158 215Q209 226 218 252L225 300Z" fill="url(#shirt)"/>{ears}<ellipse cx="80" cy="130" rx="9" ry="16" fill="{skin}"/><ellipse cx="179" cy="130" rx="9" ry="16" fill="{skin}"/><path d="{jaw}" fill="{skin}"/><path d="M92 118Q105 111 115 118M146 118Q158 111 170 118" fill="none" stroke="{h}" stroke-width="3" stroke-linecap="round"/><g fill="#eae4e2"><ellipse cx="104" cy="132" rx="12" ry="7"/><ellipse cx="158" cy="132" rx="12" ry="7"/></g><g fill="{eye}"><ellipse cx="104" cy="132" rx="5" ry="7"/><ellipse cx="158" cy="132" rx="5" ry="7"/></g><g fill="#242333"><ellipse cx="104" cy="132" rx="2" ry="5"/><ellipse cx="158" cy="132" rx="2" ry="5"/></g><g fill="#fff"><circle cx="106" cy="130" r="2"/><circle cx="160" cy="130" r="2"/></g><path d="M129 137L125 153L133 154" fill="none" stroke="#7f514a" stroke-opacity=".35" stroke-width="2"/><path d="M116 170Q130 176 144 169" fill="none" stroke="#9e6468" stroke-width="2.5" stroke-linecap="round"/><path d="{front}" fill="{h}"/>{accessories}</svg>'''
