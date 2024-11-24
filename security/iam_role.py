import pulumi
from pulumi_aws import iam
from pulumi import ComponentResource, ResourceOptions

class IAMRole(ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__("custom:security:IAMRole", name, None, opts)

        self.role = iam.Role(f"{name}-role",
            assume_role_policy='''{
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }''',
            opts=ResourceOptions(parent=self)
        )
        
        self.instance_profile = iam.InstanceProfile(f"{name}-profile",
            role=self.role.name,
            opts=ResourceOptions(parent=self)
        )
        
        self.arn = self.instance_profile.name

        self.register_outputs({
            "role_arn": self.role.arn,
            "instance_profile": self.instance_profile.name
        })
