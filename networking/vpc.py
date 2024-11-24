from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class VPCStack(ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__("custom:networking:VPCStack", name, None, opts)

        # Create VPC
        self.vpc = aws.ec2.Vpc(f"{name}-vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={"Name": f"{name}-vpc"},
            opts=ResourceOptions(parent=self)
        )

        # Get available AZs
        azs = aws.get_availability_zones(state="available").names

        # Create public subnets
        self.public_subnets = []
        for i, az in enumerate(azs[:2]):  # Using 2 AZs for us-west-1
            subnet = aws.ec2.Subnet(f"{name}-public-{i+1}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i*32}.0/20",
                availability_zone=az,
                map_public_ip_on_launch=True,
                tags={
                    "Name": f"{name}-public-{i+1}",
                    "kubernetes.io/role/elb": "1"
                },
                opts=ResourceOptions(parent=self)
            )
            self.public_subnets.append(subnet)

        # Create private subnets
        self.private_subnets = []
        for i, az in enumerate(azs[:2]):  # Using 2 AZs for us-west-1
            subnet = aws.ec2.Subnet(f"{name}-private-{i+1}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{(i*32)+16}.0/20",
                availability_zone=az,
                tags={
                    "Name": f"{name}-private-{i+1}",
                    "kubernetes.io/role/internal-elb": "1"
                },
                opts=ResourceOptions(parent=self)
            )
            self.private_subnets.append(subnet)

        # Create Internet Gateway
        self.igw = aws.ec2.InternetGateway(f"{name}-igw",
            vpc_id=self.vpc.id,
            tags={"Name": f"{name}-igw"},
            opts=ResourceOptions(parent=self)
        )

        # Create EIP for NAT Gateway
        self.eip = aws.ec2.Eip(f"{name}-nat-eip",
            domain="vpc",
            tags={"Name": f"{name}-nat-eip"},
            opts=ResourceOptions(parent=self)
        )

        # Create NAT Gateway
        self.nat_gateway = aws.ec2.NatGateway(f"{name}-nat",
            allocation_id=self.eip.id,
            subnet_id=self.public_subnets[0].id,
            tags={"Name": f"{name}-nat"},
            opts=ResourceOptions(parent=self)
        )

        # Create route tables
        self.public_rt = aws.ec2.RouteTable(f"{name}-public-rt",
            vpc_id=self.vpc.id,
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "gateway_id": self.igw.id
            }],
            tags={"Name": f"{name}-public-rt"},
            opts=ResourceOptions(parent=self)
        )

        self.private_rt = aws.ec2.RouteTable(f"{name}-private-rt",
            vpc_id=self.vpc.id,
            routes=[{
                "cidr_block": "0.0.0.0/0",
                "nat_gateway_id": self.nat_gateway.id
            }],
            tags={"Name": f"{name}-private-rt"},
            opts=ResourceOptions(parent=self)
        )

        # Associate route tables with subnets
        for i, subnet in enumerate(self.public_subnets):
            aws.ec2.RouteTableAssociation(f"{name}-public-rta-{i+1}",
                subnet_id=subnet.id,
                route_table_id=self.public_rt.id,
                opts=ResourceOptions(parent=self)
            )

        for i, subnet in enumerate(self.private_subnets):
            aws.ec2.RouteTableAssociation(f"{name}-private-rta-{i+1}",
                subnet_id=subnet.id,
                route_table_id=self.private_rt.id,
                opts=ResourceOptions(parent=self)
            )

        # Export values
        self.vpc_id = self.vpc.id
        self.private_subnet_ids = [subnet.id for subnet in self.private_subnets]
        self.public_subnet_ids = [subnet.id for subnet in self.public_subnets]


        self.register_outputs({
            "vpc_id": self.vpc.id,
            "private_subnet_ids": self.private_subnet_ids,
            "public_subnet_ids": self.public_subnet_ids
        })

