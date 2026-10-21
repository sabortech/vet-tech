"""Explicit synthetic-fixture verification; read deployment-review.md before use.
Tokens, records and screenshots remain in the private run directory.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    import sys
    from concurrent.futures import ThreadPoolExecutor
    from datetime import datetime,timedelta,timezone
    from uuid import uuid4
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    a,c=(s.data['pets'][key] for key in ('a','c'))

    def book(name,actor,pet='a',vet='va',hour='12:00',offset=5):
        result=s.ok(name,'POST','tutor/consultas',actor,{'payload':s.booking(pet,vet,hour,offset)})
        s.track('consulta',result)
        return result['id']

    # Another professional may read the same pet but cannot write someone else's consult.
    book('grant_second_vet','ta',vet='vb',hour='13:00')
    consult=s.data['created']['consulta'][0]
    s.deny('authorized_other_vet_cannot_write','PUT',f'veterinario/consultas/{consult}/rascunho','vb',{'versao':0,'payload':{}})

    def race(name,payloads):
        def send(item):
            actor,payload=item
            return s.api('POST','tutor/consultas',actor,{'payload':payload})
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(send,payloads))
        statuses=[item[0] for item in results]
        print({'race':name,'statuses':statuses},flush=True)
        s.check(name+'_one_winner',sum(x in (200,201) for x in statuses)==1)
        s.check(name+'_business_conflict',sum(x in (400,409) for x in statuses)==1)

    race('concurrent_vet_slot',[('ta',s.booking('a','va','14:00',5)),('tb',s.booking('c','va','14:00',5))])
    race('concurrent_pet_slot',[('tb',s.booking('c','va','15:00',5)),('tb',s.booking('c','vb','15:00',5))])
    same=s.booking('a','va','16:00',5)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:s.api('POST','tutor/consultas','ta',{'payload':same}),range(2)))
    s.check('concurrent_same_operation_single_id',all(status in (200,201) for status,_ in results) and results[0][1]['id']==results[1][1]['id'])
    s.discover()
    print({'concurrency':'passed'},flush=True)



if __name__ == "__main__":
    main()
