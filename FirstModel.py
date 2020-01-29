import random
import functools
import numpy as np
import simpy
import matplotlib.pyplot as plt
'''
    Threading while adding to queue must me implemented for result consistency
'''


from SimComponents import PacketGenerator, PacketSink, SwitchPort, RandomBrancher


# Create the packet generators and sink

# selector is some kind of an indetifier(unique label) for each generator, we need it to retrieve this very generated flow in output
def selector1(pkt):
    return pkt.src == "Src1"


# def selector2(pkt):
# return pkt.src == "Source2"

# Paretovariate() function of the random module by default accepts just one parameter - shape of the distribution (alpha),but assumes the location parameter(Xm) as 1.
def my_paretovariate(alpha, xm=1.1):
    """
    Sample Pareto variate with arbitrary xm
    """
    return xm * random.paretovariate(alpha)


if __name__ == '__main__':
    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters.
    # each call to these will produce a new random value.
    mean_pkt_size = 850  # in bytes
    adist1 = functools.partial(random.expovariate, 0.04375) #(1/40 + 1/16)/2
    adist2 = functools.partial(random.expovariate, 0.04375) #(1/40 + 1/16)/2
    # The same distribution of pkt sizes for both.
    sdist = functools.partial(my_paretovariate, 81.5) # xm = 1.1 alpha = 81.5
    #sdist = functools.partial(random.expovariate, 1.0 / mean_pkt_size)
    samp_dist = functools.partial(random.expovariate, 0.04375)
    # The same port rate  for all routers
    port_rate = 100 / 8 * 10**6  # 100Mbit/s
    qlim = 4 * 10**6 #4Mb

    # Create the SimPy environment. This is the thing that runs the simulation.
    env = simpy.Environment()

    ps1 = PacketSink(env, debug=False, rec_arrivals=True)
    # figure out the use of selector
    # ps1 = PacketSink(env, debug=False, rec_arrivals=True)
    pg1 = PacketGenerator(env, 'src1', adist1, sdist)
    pg2 = PacketGenerator(env, 'src2', adist2, sdist)
    branch1 = RandomBrancher(env, [0.50, 0.50])
    branch2 = RandomBrancher(env, [0.50, 0.50])
    #pseudoBrancher
    branch3 = RandomBrancher(env, [1.00, 0.00])
    switch_port1 = SwitchPort(env, port_rate,qlimit=qlim)
    switch_port2 = SwitchPort(env, port_rate,qlimit=qlim)
    switch_port3 = SwitchPort(env, port_rate,qlimit=qlim)
    switch_port4 = SwitchPort(env, port_rate,qlimit=qlim)
    switch_port5 = SwitchPort(env, port_rate,qlimit=qlim)

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

    switch_port4.out = branch3
    branch3.outs[0] = switch_port5

    switch_port5.out = ps1
    # Run it
    env.run(until=1000000)
    print(ps1.waits[-10:])
    # print pm.sizes[-10:]
    print("average wait {}".format(sum(ps1.waits) / len(ps1.waits)))
    print("packets sent {}".format(pg1.packets_sent + pg2.packets_sent))
    print("packets received: {}".format(len(ps1.waits)))

    fig, axis = plt.subplots()
    axis.hist(ps1.waits, bins=100, normed=True)
    axis.set_title("Histogram for waiting times")
    axis.set_xlabel("time")
    axis.set_ylabel("normalized frequency of occurrence")
    fig.savefig("WaitHistogram.png")
    plt.show()