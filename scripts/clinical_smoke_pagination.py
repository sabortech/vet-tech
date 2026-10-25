"""Explicit synthetic-fixture verification; read deployment-review.md before use.
Tokens, records and screenshots remain in the private run directory.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    import sys
    from datetime import datetime,timezone,timedelta
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    rows=[r for r in s.store.pages(s.store.url('consulta')) if r['pet_id'] in s.data['pets'].values()]
    vet=s.data['actors']['va']['id']
    # Administrative fixture setup only: put every still-pending synthetic slot under
    # one synthetic professional, without changing any finalized consultation.
    for row in rows:
     if row['status']=='agendada' and row['veterinario_id']!=vet:
      _,status=s.store.write('PUT','consulta',{'veterinario_id':vet},row['id'])
      s.check('pagination_fixture_assignment_'+str(row['id']),status==200)
    for i in range(30-len(rows)):
     payload=s.booking(hour=f'08:{i+1:02d}',offset=9)
     response=s.ok('pagination_booking_'+str(i+1),'POST','tutor/consultas','ta',{'payload':payload})
     s.track('consulta',response)
    first=s.ok('pagination_page_one','GET','veterinario/agenda?page=1','va')
    second=s.ok('pagination_page_two','GET','veterinario/agenda?page=2','va')
    s.check('real_pagination_25_plus_1',len(first['items'])==25 and len(second['items'])==1 and first['total']==26)
    combined=first['items']+second['items']
    s.check('chronological_across_pages',[r['agendada_para'] for r in combined]==sorted(r['agendada_para'] for r in combined))
    day=(datetime.now(timezone.utc)+timedelta(days=9)).date().isoformat()
    agenda=s.ok('daily_timeline_data','GET',f'veterinario/agenda?dia={day}','va')
    s.check('daily_calendar_matches_same_reservations',all(any(r['id']==c['id'] for r in combined) for c in agenda['items']))
    pending=next(r for r in combined if r['status']=='agendada')
    past=int((datetime.now(timezone.utc)-timedelta(days=2)).timestamp()*1000)
    s.store.write('PUT','consulta',{'agendada_para':past},pending['id'])
    late=s.ok('late_pending_appointments','GET','veterinario/agenda','va')
    s.check('late_scheduled_remains_accessible',any(r['id']==pending['id'] for r in late['items']))
    s.discover()


if __name__ == "__main__":
    main()
