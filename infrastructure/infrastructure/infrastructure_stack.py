#!/usr/bin/python3

from aws_cdk import (
    # Duration,
    Stack,
    CfnTag as CfnTag,
    aws_ec2 as ec2,
    aws_efs as efs,
)
from constructs import Construct

class InfrastructureStack(Stack):
    def _define_efs(self):
        self.file_system = efs.FileSystem(
            scope=self,
            id="Efs",
            vpc=self.vpc, one_zone=True,
            file_system_name="Kube"
        )

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc_name = "vpc-k8s-1"
        self.vpc_cidr = '192.168.0.0/16'

        self._define_vpc()
        self._define_efs()

        sec_group = ec2.SecurityGroup(self, "K8S_Sec_Group", vpc=self.vpc, allow_all_outbound=True)

        sec_group.add_ingress_rule( ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(6443), "Allow Kubeket access")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(2379), "Allow etcd port")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10279), "Kube-controller manager")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10259), "Kube scheduler")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10250), "Kubelet port")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(8080), "Kubelet port")

        # Create EC2 instance
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/README.html
        # https://docs.aws.amazon.com/linux/al2023/ug/what-is-amazon-linux.html
                # Create Key Pair
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnKeyPair.html

        # If you don't have an existing key pair, uncomment this code to create a key pair

  
        key_pair = ec2.KeyPair(self, "roy-run2",
                #FLip comments if you want to generate a new key pair 
                #type=ec2.KeyPairType.RSA, format=ec2.KeyPairFormat.PEM,
                               public_key_material=open('/home/ec2-user/.ssh/id2_rsa.pub').read()
        )

        control_instance = ec2.Instance(
            self,
            "Control_plane",
            instance_type=ec2.InstanceType("t2.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC), 
            security_group=sec_group,
            associate_public_ip_address=True,
            key_pair=key_pair
        )
        u_control_instance = ec2.Instance(
            self,
            "ubuntu_Control_plane",
            instance_type=ec2.InstanceType("t2.medium"),
            machine_image=ec2.MachineImage.generic_linux({ 'eu-west-1' : 'ami-0776c814353b4814d'}),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC), 
            security_group=sec_group,
            associate_public_ip_address=True,
            key_pair=key_pair
        )

        compute_instance = ec2.Instance(
            self,
            "Compute_plane",
            instance_type=ec2.InstanceType("t2.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            #Security hint: in production, the compute machines should be in private subnet
            #vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS), 
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            vpc=self.vpc,
            security_group=sec_group,
            associate_public_ip_address=True,
            key_pair=key_pair
        )
        u_compute_instance = ec2.Instance(
            self,
            "Ubuntu_Compute_plane",
            instance_type=ec2.InstanceType("t2.medium"),
            machine_image=ec2.MachineImage.generic_linux({ 'eu-west-1' : 'ami-0776c814353b4814d'}),
            #Security hint: in production, the compute machines should be in private subnet
            #vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS), 
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            vpc=self.vpc,
            security_group=sec_group,
            associate_public_ip_address=True,
            key_pair=key_pair
        )
        #Now connect the EC2 instances to the Kube file system
        self.file_system.connections.allow_default_port_from(control_instance)
        self.file_system.connections.allow_default_port_from(compute_instance)
        compute_instance.user_data.add_commands("yum check-update -y", "yum upgrade -y", "yum install -y amazon-efs-utils", "yum install -y nfs-utils", "file_system_id_1=" + self.file_system.file_system_id, "efs_mount_point_1=/mnt/kube", "mkdir -p \"${efs_mount_point_1}\"", "test -f \"/sbin/mount.efs\" && echo \"${file_system_id_1}:/ ${efs_mount_point_1} efs defaults,_netdev\" >> /etc/fstab || " + "echo \"${file_system_id_1}.efs." + Stack.of(self).region + ".amazonaws.com:/ ${efs_mount_point_1} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0\" >> /etc/fstab", "mount -a -t efs,nfs4 defaults")

        control_instance.user_data.add_commands("yum check-update -y", "yum upgrade -y", "yum install -y amazon-efs-utils", "yum install -y nfs-utils", "file_system_id_1=" + self.file_system.file_system_id, "efs_mount_point_1=/mnt/kube", "mkdir -p \"${efs_mount_point_1}\"", "test -f \"/sbin/mount.efs\" && echo \"${file_system_id_1}:/ ${efs_mount_point_1} efs defaults,_netdev\" >> /etc/fstab || " + "echo \"${file_system_id_1}.efs." + Stack.of(self).region + ".amazonaws.com:/ ${efs_mount_point_1} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0\" >> /etc/fstabo", "mount -a -t efs,nfs4 defaults")


    def _define_vpc(self):
        vpc_construct_id = 'vpc'
        self.vpc = ec2.Vpc(self, vpc_construct_id, vpc_name=self.vpc_name,
                      ip_addresses=ec2.IpAddresses.cidr(self.vpc_cidr),
                      max_azs=2,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(subnet_type=ec2.SubnetType.PUBLIC,
                                                  name='Public', cidr_mask=20),
                          ec2.SubnetConfiguration(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                                                  name='Compute',
                                                  cidr_mask=20)])



        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "InfrastructureQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
