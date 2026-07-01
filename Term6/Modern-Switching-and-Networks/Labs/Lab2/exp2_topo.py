from mininet.topo import Topo

class Exp2Topo(Topo):
    def build(self):
        # 核心交换机，固定 dpid
        s1 = self.addSwitch('s1', dpid='0000000000000001')

        # 接入交换机
        s2 = self.addSwitch('s2', dpid='0000000000000002')
        s3 = self.addSwitch('s3', dpid='0000000000000003')
        s4 = self.addSwitch('s4', dpid='0000000000000004')

        # 主机，固定 IP 和 MAC
        h1 = self.addHost('h1', ip='10.0.0.1/8', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/8', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/8', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/8', mac='00:00:00:00:00:04')
        h5 = self.addHost('h5', ip='10.0.0.5/8', mac='00:00:00:00:00:05')
        h6 = self.addHost('h6', ip='10.0.0.6/8', mac='00:00:00:00:00:06')

        # 核心交换机与接入交换机连接
        # s1-eth1 <-> s2
        # s1-eth2 <-> s3
        # s1-eth3 <-> s4
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s4)

        # 接入交换机与主机连接
        # s2-eth2 <-> h1
        # s2-eth3 <-> h2
        self.addLink(s2, h1)
        self.addLink(s2, h2)

        # s3-eth2 <-> h3
        # s3-eth3 <-> h4
        self.addLink(s3, h3)
        self.addLink(s3, h4)

        # s4-eth2 <-> h5
        # s4-eth3 <-> h6
        self.addLink(s4, h5)
        self.addLink(s4, h6)

topos = {
    'exp2topo': Exp2Topo
}