"""Ensure incomplete/stale/mismatched sprite-order evidence blocks publishing."""
import copy
from api_sprite_order_proofs import SITE,read,verify_reports

state=read(SITE/'verification/api-sprite-order/state/results.json')
visual=read(SITE/'verification/api-sprite-order/example/results.json')
verify_reports(state,visual)
def reject(label,mutate):
    a,b=copy.deepcopy(state),copy.deepcopy(visual)
    mutate(a,b)
    try:verify_reports(a,b)
    except AssertionError:
        print('Rejected:',label)
    else:raise AssertionError('Accepted invalid evidence: '+label)

reject('missing ABI run',lambda a,b:a['records'].pop())
reject('duplicate numeric mode',lambda a,b:a['records'].__setitem__(0,a['records'][1]))
reject('failed memory case',lambda a,b:a['records'][0]['cases'][0]['actual'].__setitem__(0,0))
reject('wrong completion state',lambda a,b:a['records'][0]['status'].__setitem__(7,0))
reject('wrong case identity',lambda a,b:a['records'][0]['cases'][0].__setitem__('name','unknown'))
reject('stale library',lambda a,b:a['library_sha256'].__setitem__('sprite_order.c','0'*64))
reject('missing moving capture',lambda a,b:b['records'].pop())
reject('duplicate visual mode',lambda a,b:b['records'].__setitem__(0,b['records'][1]))
reject('wrong square selection',lambda a,b:b['records'][0]['selected_squares'].__setitem__(0,11))
reject('pixel mismatch',lambda a,b:b['records'][0].__setitem__('sprite_pixel_mismatches',1))
reject('label mismatch',lambda a,b:b['records'][0].__setitem__('label_pixel_mismatches',1))
reject('stale image',lambda a,b:b['records'][0].__setitem__('image_sha256','0'*64))
reject('stale source',lambda a,b:b['records'][0].__setitem__('source_sha256','0'*64))
reject('stale checker',lambda a,b:b.__setitem__('script_sha256','0'*64))
print('Valid matrix accepted; fourteen corruptions rejected')
