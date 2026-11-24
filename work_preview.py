"""Chief-only work sandbox in one bot; public rollout is a separate saved switch."""
import copy


def enabled(user, chief):
    return user.get('_telegram_id')==chief and user.get('work_preview_enabled',True)


def profile(user, chief):
    if user.get('_work_sandbox') or not enabled(user,chief):
        return user
    result=user.get('work_preview_profile')
    if not isinstance(result,dict):
        result=dict(_telegram_id=chief,_work_sandbox=True,bucks=10000,lang=user.get('lang','ru'),
                    verified=True,agreement_accepted=True,personality_ready=True,gender=user.get('gender','female'))
        user['work_preview_profile']=result
    # Only display language and current entitlement multipliers follow the real account.
    result['lang']=user.get('lang','ru')
    result['subscription']=copy.deepcopy(user.get('subscription') or {})
    result['work_boost_until']=user.get('work_boost_until')
    return result


def version_two(user, settings):
    return bool(user.get('_work_sandbox') or settings.get('work_games_v2'))
