"""Persistent support queue, FIFO within priority; old tickets cannot starve."""
import time


def tickets(settings):
    return settings.setdefault('support_tickets_v1', {})


def active(settings):
    now = time.time()
    return sorted((t for t in tickets(settings).values() if t['status'] != 'resolved'),
                  key=lambda t: (t['status'] != 'in_progress', not (t['priority'] or now-t['created_at'] >= 86400), t['created_at'], int(t['id'])))


def submit(settings, uid, text, priority=False):
    queue = tickets(settings)
    ticket = next((t for t in queue.values() if t['user_id'] == int(uid) and t['status'] != 'resolved'), None)
    if ticket is None:
        ident = str(int(settings.get('support_ticket_sequence', 0)) + 1)
        settings['support_ticket_sequence'] = int(ident)
        ticket = dict(id=ident, user_id=int(uid), created_at=time.time(), status='waiting', priority=bool(priority), messages=[])
        queue[ident] = ticket
    ticket['messages'] = (ticket['messages'] + [text[:3000]])[-20:]
    ticket['priority'] = bool(priority)
    return ticket


def snapshot(settings, uid):
    for i, ticket in enumerate(active(settings)):
        if ticket['user_id'] == int(uid):
            return dict(id=ticket['id'], position=i+1, status=ticket['status'], priority=ticket['priority'])
    return None


def claim(settings, ident, admin):
    ticket = tickets(settings).get(str(ident))
    if not ticket or ticket['status'] == 'resolved':
        return False
    if ticket['status'] == 'in_progress':
        return ticket.get('admin') == int(admin)
    waiting = [t for t in active(settings) if t['status'] == 'waiting']
    if not waiting or waiting[0]['id'] != ticket['id']:
        return False
    ticket.update(status='in_progress', admin=int(admin))
    return True


def resolve(settings, ident, admin):
    ticket = tickets(settings).get(str(ident))
    if ticket and ticket['status'] == 'in_progress' and ticket.get('admin') == int(admin):
        ticket.update(status='resolved', resolved_at=time.time())
        # Retain a bounded audit trail, never evict an active ticket.
        closed = sorted((t for t in tickets(settings).values() if t['status']=='resolved'), key=lambda t:t['resolved_at'])
        for old in closed[:-500]:
            del tickets(settings)[old['id']]
        return True
    return False
