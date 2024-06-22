#!/usr/bin/python3

from aws_cdk import (
    # Duration,
    Stack,
    CfnTag as CfnTag,
    aws_ec2 as ec2,
)
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc_name = "vpc-k8s-1"
        self.vpc_cidr = '192.168.0.0/16'

        self._define_vpc()

        sec_group = ec2.SecurityGroup(self, "K8S_Sec_Group", vpc=self.vpc, allow_all_outbound=True)

        sec_group.add_ingress_rule( ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(6443), "Allow Kubeket access")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(2379), "Allow etcd port")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10279), "Kube-controller manager")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10259), "Kube scheduler")
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10250), "Kubelet port")

        # Create EC2 instance
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/README.html
        # https://docs.aws.amazon.com/linux/al2023/ug/what-is-amazon-linux.html
                # Create Key Pair
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnKeyPair.html

        # If you don't have an existing key pair, uncomment this code to create a key pair

  
        key_pair = ec2.KeyPair(self, "roy-run1",
                type=ec2.KeyPairType.RSA, format=ec2.KeyPairFormat.PEM)

        control_instance = ec2.Instance(
            self,
            "Control_plane",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC), 
            security_group=sec_group,
            associate_public_ip_address=True,
            key_pair=key_pair
        )
        compute_instance = ec2.Instance(
            self,
            "Compute_plane",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS), 
            vpc=self.vpc,
            security_group=sec_group,
            associate_public_ip_address=False,
            key_pair=key_pair
        )

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
