:  Vector stream of events

NEURON {
	ARTIFICIAL_CELL VecStim
}

ASSIGNED {
	index
	etime (ms)
	space
}

INITIAL {
	index = 0
	:element()
	if (index > 0) {
		net_send(etime - t, 1)
	}
}

NET_RECEIVE (w) {
	if (flag == 1) {
		net_event(t)
		:element()
		if (index > 0) {
			net_send(etime - t, 1)
		}
	}
}









