"""Recent-dialogue photo planning: preserve safe pose, perspective, identity and clothes."""
import profile_options,scene_photos,fandom_catalog

def recent(user):
 return [{'role':m['role'],'text':str(m.get('content',''))[:1600]} for m in user.get('history',[]) if m.get('role') in ('user','assistant') and m.get('content') and not m.get('card') and not m.get('photo') and str(m['content']).strip()!='📷'][-12:]
def instruction(user,level,appearance,pov_tags=''):
 return (scene_photos.INSTRUCTION+' Selected appearance overrides older descriptions: '+appearance+'. Clothing must remain '+profile_options.clothing_facts(user,level)+'. Use the most recent visible pose. Return JSON only with allowed:true, setting, lighting, pose, framing, expression. Do not write freeform image instructions.')
def render_prompt(user,appearance,raw,context,level):
 return scene_photos.portrait_prompt(appearance,user.get('gender'),raw,world=user.get('world'),outfit=profile_options.clothing_facts(user,level),race=user.get('race'),context=context,allow_romance=not fandom_catalog.family_friendly(user))
def avatar_prompt(user,appearance,context,level):
 world='natural realistic character image' if user.get('world')=='realism' else 'highly detailed anime illustration'
 return (world+'. Exactly one adult '+profile_options.photo_subject(user.get('race','human'),user.get('gender'))+', age 25+. Complete full-length character, head and shoes fully visible, generous margins. Selected appearance: '+appearance+'. '+profile_options.clothing_facts(user,level)+'. '+context+
 '. Non-explicit fashion scene in one continuous uninterrupted composition. Depict this character exactly once, face and body in the same scene.')
