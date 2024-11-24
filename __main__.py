import pulumi
from networking.vpc import VPCStack
from security.security_group import SecurityGroup
from security.iam_role import IAMRole
from ec2.instance import EC2Instance
from pulumi import ComponentResource, ResourceOptions


# Create a stack that will be the parent of all resources
class InfrastructureStack(ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__("custom:infrastructure:Stack", name, None, opts)

        # Create VPC and networking components
        self.vpc_stack = VPCStack("apex", 
            opts=ResourceOptions(parent=self))

        # Create the security group using the VPC ID
        self.security_group = SecurityGroup("apex",
            vpc_id=self.vpc_stack.vpc.id,
            opts=ResourceOptions(parent=self))

        # Create the IAM role
        self.iam_role = IAMRole("apex",
            opts=ResourceOptions(parent=self))

        # Create the EC2 instance using the first public subnet
        self.ec2_instance = EC2Instance("apex",
            vpc_stack=self.vpc_stack,
            subnet_id=self.vpc_stack.public_subnet_ids[0],
            security_group_id=self.security_group.id,
            iam_role_arn=self.iam_role.arn,
            opts=ResourceOptions(parent=self))

        self.register_outputs({
            "vpc_id": self.vpc_stack.vpc.id,
            "instance_id": self.ec2_instance.id
        })

# Create the main stack
stack = InfrastructureStack("apex")

# Export important values
pulumi.export('vpc_id', stack.vpc_stack.vpc.id)
pulumi.export('instance_id', stack.ec2_instance.id)