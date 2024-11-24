import pulumi
from pulumi_aws import ec2
from pulumi import ComponentResource, ResourceOptions

# security/security_group.py
class SecurityGroup(ComponentResource):
    def __init__(self, name, vpc_id, opts=None):
        super().__init__("custom:security:SecurityGroup", name, None, opts)

        self.group = ec2.SecurityGroup(f"{name}-sg",
            description='Allow HTTP and SSH',
            vpc_id=vpc_id,
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    protocol='tcp',
                    from_port=80,
                    to_port=80,
                    cidr_blocks=['0.0.0.0/0'],
                ),
                ec2.SecurityGroupIngressArgs(
                    protocol='tcp',
                    from_port=22,
                    to_port=22,
                    cidr_blocks=['0.0.0.0/0'],
                ),
            ],
            egress=[
                ec2.SecurityGroupEgressArgs(
                    protocol='-1',
                    from_port=0,
                    to_port=0,
                    cidr_blocks=['0.0.0.0/0'],
                ),
            ],
            opts=ResourceOptions(parent=self)
        )
        self.id = self.group.id
        
        self.register_outputs({
            "security_group_id": self.id
        })
