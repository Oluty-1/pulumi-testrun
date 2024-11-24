import pulumi
from pulumi_aws import ec2
from pulumi import ComponentResource, ResourceOptions

class EC2Instance(ComponentResource):
    def __init__(self, name, vpc_stack, subnet_id, security_group_id, iam_role_arn, opts=None):
        super().__init__("custom:compute:EC2Instance", name, None, opts)

        self.instance = ec2.Instance(f"{name}-instance",
            instance_type='t2.micro',
            ami='ami-0819a8650d771b8be',
            subnet_id=subnet_id,
            vpc_security_group_ids=[security_group_id],
            iam_instance_profile=iam_role_arn,
            tags={
                "Name": f"{name}-instance"
            },
            opts=ResourceOptions(parent=self)
        )
        self.id = self.instance.id

        self.register_outputs({
            "instance_id": self.id,
            "private_ip": self.instance.private_ip,
            "public_ip": self.instance.public_ip
        })
