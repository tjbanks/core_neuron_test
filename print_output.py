import h5py
spikes = h5py.File('output/spikes.h5')

node_ids = list(spikes['spikes']['biophysical']['node_ids'])
spikes = list(spikes['spikes']['biophysical']['timestamps'])

print(node_ids)
print(spikes)