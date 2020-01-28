
import random
import functools
import numpy as np
import simpy

from SimComponents import PacketGenerator, PacketSink, SwitchPort, RandomBrancher


if __name__ == '__main__':
    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters.
    # each call to these will produce a new random value.
    mean_pkt_size = 100.0  # in bytes
    adist1 = functools.partial(random.expovariate, 0.025)
    adist2 = functools.partial(random.expovariate, 0.0625)
    # The same distribution of pkt sizes for both.
    sdist = functools.partial(random.expovariate, 1.0/mean_pkt_size)
    # The same port rate  for all routers
    port_rate = 2.5*8*mean_pkt_size

    # Create the SimPy environment. This is the thing that runs the simulation.
    env = simpy.Environment()

    # Create the packet generators and sink
    def selector1(pkt):
        return pkt.src == "Src1"

    #Paretovariate() function of the random module by default accepts just one parameter - shape of the distribution (alpha),but assumes the location parameter(Xm) as 1.
    def my_paretovariate(alpha, xm=1.0):
        """
        Sample Pareto variate with arbitrary xm
        """
        return xm * random.paretovariate(alpha)
    #def selector2(pkt):
        #return pkt.src == "Source2"

    ps1 = PacketSink(env, debug=False, rec_arrivals=True, selector=selector1)
    #figure out the use of selector
    #ps1 = PacketSink(env, debug=False, rec_arrivals=True)
    pg1 = PacketGenerator(env, "Src1", adist1, sdist)
    pg2 = PacketGenerator(env, "Src2", adist2, sdist)
    branch1 = RandomBrancher(env, [0.50, 0.50])
    branch2 = RandomBrancher(env, [0.50, 0.50])
    #pseudoBrancher
    branch3 = RandomBrancher(env, [1.00, 0.00])
    switch_port1 = SwitchPort(env, port_rate)
    switch_port2 = SwitchPort(env, port_rate)
    switch_port3 = SwitchPort(env, port_rate)
    switch_port4 = SwitchPort(env, port_rate)
    switch_port5 = SwitchPort(env, port_rate)

    # Wire packet generators, switch ports, and sinks together
    pg1.out = switch_port1
    switch_port1.out = branch1
    branch1.outs[0] = switch_port3
    branch1.outs[1] = switch_port4
    pg2.out = switch_port2
    switch_port2.out = branch2
    branch2.outs[0] = switch_port3
    branch2.outs[1] = switch_port4

    switch_port3.out = branch3
    branch3.outs[0] = switch_port5

    switch_port3.out = branch3
    branch3.outs[0] = switch_port5

    switch_port5.out = ps1
    # Run it
    env.run(until=1000000)
    print(ps1.waits[-10:])
    # print pm.sizes[-10:]
    print("average wait {}".format(sum(ps1.waits)/len(ps1.waits)))
    print("packets sent {}".format(pg1.packets_sent + pg2.packets_sent))
    print("packets received: {}".format(len(ps1.waits)))
    #print "average system occupancy: {}".format(float(sum(pm.sizes))/len(pm.sizes))
