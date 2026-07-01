from mininet.topo import Topo

class Exp1Topo(Topo):
    def build(self):
        # 添加主机
        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')
        h4 = self.addHost('h4', ip='10.0.0.4/8')
        h5 = self.addHost('h5', ip='10.0.0.5/8')
        h6 = self.addHost('h6', ip='10.0.0.6/8')

        # 添加交换机
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # 主机与接入交换机连接
        self.addLink(h1, s2)
        self.addLink(h2, s2)

        self.addLink(h3, s3)
        self.addLink(h4, s3)

        self.addLink(h5, s4)
        self.addLink(h6, s4)

        # 交换机之间连接：s1 作为核心交换机
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s4)

topos = {
    'exp1topo': Exp1Topo
}