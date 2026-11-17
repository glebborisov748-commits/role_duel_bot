"""The human player's visual identity is separate from their AI companion."""
import character_options
import profile_options


def validate(body):
    gender=body.get('gender')
    world=body.get('world')
    if gender not in ('male','female') or world not in ('anime','realism'):
        raise ValueError('Invalid avatar')
    name=body.get('name','')
    if not isinstance(name,str) or len(name)>60:raise ValueError('Invalid name')
    if not isinstance(body.get('use_photo_appearance',True),bool):raise ValueError('Invalid photo setting')
    raw=character_options.validate(body.get('appearance',{}),gender)
    return {'name':name.strip(),'gender':gender,'world':world,'use_photo_appearance':body.get('use_photo_appearance',True),
            'race':profile_options.validate_race(body.get('race','human')),
            'appearance':{k:raw[k] for k in character_options.VISUAL_KEYS}}


def facts(person):
    gender='man' if person.get('gender')=='male' else 'woman'
    if person.get('avatar') and person.get('use_photo_appearance',True):
        return 'adult '+gender+', age 25+, preserve the exact visible face, hairstyle, hair color, skin tone and eyes from this person’s reference photo; do not replace them with preset features'
    return 'adult '+gender+', age 25+, '+(character_options.appearance(person) or 'human')


def couple_prompt(player,companion,action):
    # Couple generation never inherits the single-portrait "solo / no second person" rules.
    outfits=profile_options.WARDROBE.get(companion.get('wardrobe_outfit'),{}).get('fact','casual clothing')
    return ('Create ONE coherent '+('realistic photograph' if companion.get('world')=='realism' else 'anime illustration')+
            ' of EXACTLY TWO distinct fully clothed adults aged 25+. '
            'Reference image 1 is the PLAYER: '+facts(player)+'. '
            'Reference image 2 is the COMPANION: '+facts(companion)+', wearing '+outfits+'. '
            'Use each reference as a distinct facial identity, then apply the listed selected gender, hairstyle, hair color, skin and eyes separately; selected attributes override preset colors. '
            'Never swap identities, copy one face onto both people, add a third person, or merge bodies. '
            'Natural anatomical interaction, both faces visible. Non-explicit affectionate scene. '
            'Action: '+action+'. Keep clothes on. No nudity or sexual activity. No text, panels or collage.')
