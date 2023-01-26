import h5py
spikes = h5py.File('output/spikes.h5')
#v_report = h5py.File('output/v_report.h5')
try:
    node_ids = list(spikes['spikes']['biophysical']['node_ids'])
    spikes = list(spikes['spikes']['biophysical']['timestamps'])

    print(node_ids)
    print(spikes)
except:
    import pdb;pdb.set_trace()
