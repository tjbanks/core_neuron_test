import sys
from neuron import h, gui
from neuron import coreneuron
coreneuron.enable = True
coreneuron.gpu = True

# setup model
h('''create soma''')
h.soma.L=5.6419
h.soma.diam=5.6419
h.soma.insert("hh")
h.soma.nseg = 3
ic = h.IClamp(h.soma(.25))
ic.delay = .1
ic.dur = 0.1
ic.amp = 0.3

ic2 = h.IClamp(h.soma(.75))
ic2.delay = 5.5
ic2.dur = 1
ic2.amp = 0.3

h.tstop = 10

# make sure to enable cache efficiency
h.cvode.cache_efficient(1)

pc = h.ParallelContext()
pc.set_gid2node(pc.id()+1, pc.id())
myobj = h.NetCon(h.soma(0.5)._ref_v, None, sec=h.soma)
pc.cell(pc.id()+1, myobj)


coreneuron.verbose = 3
h.stdinit()
corenrn_all_spike_t = h.Vector()
corenrn_all_spike_gids = h.Vector()
pc.spike_record(-1, corenrn_all_spike_t, corenrn_all_spike_gids )
pc.psolve(h.tstop)

# copy vector as numpy array
corenrn_all_spike_t = corenrn_all_spike_t.to_python()
corenrn_all_spike_gids = corenrn_all_spike_gids.to_python()


h.quit()