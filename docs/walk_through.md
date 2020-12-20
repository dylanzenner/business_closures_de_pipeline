# Intro
Hello, everyone! welcome to the walkthrough guide for the business_closures_de_pipeline. While building this pipeline I realised that there really isn't any good projects (That I have come across) which utilize Amazon DocumentDB as the main database. Thus, I decided to write a tutorial/walkthrough guide for my project so that others can replicate what I have done and hopefully gain some knowledge and experience which they did not have before going through this guide!

Before we begin, the building of this pipeline will be done in numerous stages so after you complete a stage feel free to take a break and come back to it later. This guide is on the long side becuase I wanted to be as detailed as possible to help lower the chance that you run into any issues along the journey. Now, without furtherado lets dive in and get started with our DocumentDB data pipeline!

# Architecture
This is the layout of the architecture we will be building:
![](DE-PROJECT.png)
I know it looks a little intimidating, but rest asured it really is not that bad once we get going.

# Stage 1: Building The VPC
Before we can really dive into the project we must first set up our VPC. I started with a blank canvous and if you are following along I recommend you do the same.

Now, let's get started:

- login to your AWS management console and from there go to the VPC dashboard.
- Click on **Elastic IPs** and **Allocate Elastic IP Address**. We will need this in order to build our VPC.
- Now, click on **VPC Dashboard** and then **launch VPC Wizard** and choose the option for **"VPC with Public and Private Subnets"**. We will need the public subnet for internet access and the private subnet for our lambda function and database.
- Next, we fill out the form with our chosen IPv4 CIDR range.
- We also need to have a CIDR range for both of our subnets (make sure that they do not overlap).
- Give a name for both of your subnets (I recommend Private and Public so we know which ones are which. We will need this information later) and **choose two different availability zones (i.e.: us-east-1a and us-east-1b)**.
- Allocate the Elastic IP address which we chose earlier
- Leave the rest set as default and choose **Create VPC**

# Stage 2: Setting Up DocumentDB
Next, we will be setting up DocumentDB and an EC2 instance in order to SSH into DocumentDB. **Warning: This is the longest part of the project so once you finish I recommend taking a break to stretch or grab a cup of coffee**.

## Step 1: Create a Subnet Group
- Open the DocumentDB dashboard and click on **Subnet Groups**
- Enter a name and description
- Now add the VPC which you created in Stage 1
- Choose the availability zone of your public subnet and then choose your subnet and click on **Add subnet** (repeat this process for your Private Subnet).
- Select **create**

## Step 2: Create a Parameter Group
- In the DocumentDB dashboard, click on **Parameter Groups**
- Enter a name for your group, select **docdb4.0** for the Family and give it a description and choose **create**

## Step 3: Create a Cluster
- In the DocumentDB dashboard choose **Clusters** and select **Create**
- Select engine version **4.0.0**
- Select Instance Class **db.t3.medium**
- Select **1** for the number of instances (Normally you would select at least 3 instances if running production. But, for this we are trying to keep costs at a minimum).
- Next fill in your authentication information and click on **Show Advanced Settings**.
- Fill in the Network settings with the VPC information we created in Stage 1, the Subnet Group we just created and the default VPC security Group (We will change this later)
- Scroll down a little to **Cluster Options** and make sure 27017 is filled in for the **Port** and the cluster parameter group we just made is selected.
- You can leave the rest as default and hit **Create Cluster**

## Step 4: Create an EC2 Instance
- Open up the EC2 dashboard and select **Launch Instance**
- Select **Amazon Linux 2 AMI (HVM), SSD Volume**
- Select **t2.micro** and choose **Next: Configure Instance Details**
- For Number of instances choose 1
- Choose the VPC we created in Stage 1 for the **Network** option
- Select the public subnet as the subnet
- Make sure that **Auto-assign Public IP** is set to **Disable** (We will be associating an Elastic IP address to this instance. That way we can stop and start our instance without having to worry about losing our IP address).
- Click on **Next: Add Storage**
- The defaults here will suffice for what we are trying to accomplish.
- Click **Next: Add Tags** and add tags if you'd like
- Click **Next: Configure Security Group**
- Make sure **Create a new security group** is selected and give it a name
- Now, we will add the following rule:

|Type|Protocol|Port Range|Source|Description|
|----|--------|----------|------|-----------|
|SSH|TCP|22|MY IP|Allows SSH Access from my IP|

- Click on **Review and Launch**
- Click on **Launch**
- Choose the key pair you'd like to launch the instance with and click **Launch Instance**

## Step 5: Associate an Elastic IP to your EC2 Instance you just launched
- In your EC2 dashboard click on **Elastic IPs**
- Click on **Allocate Elastic IP address**
- Click **Allocate**
- Now, select the EIP you just created and click on **Actions > Associate Elastic IP address**
- Make sure the **Resource type** is **Instance**, select the instance we launched and its private IP address and select **Associate**

## Step 6: SSH into the EC2 instance and install the MongoShell, Mongoexport tools, and the DocumentDB cluster certificate
- In the EC2 dashboard, select **Instances**
- Select the instance we set up earlier, click on **Connect** and follow the instructions
- Once you are SSH'd into the EC2 instance run the following command:
```
wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

```
This is the DocumentDB Certificate Authority (CA) certificate required to authenticate to your cluster.

- Run the following command in your EC2 terminal to create a repository file:
```
echo -e "[mongodb-org-4.0] \nname=MongoDB Repository\nbaseurl=https://repo.mongodb.org/yum/amazon/2013.03/mongodb-org/4.0/x86_64/\ngpgcheck=1 \nenabled=1 \ngpgkey=https://www.mongodb.org/static/pgp/server-4.0.asc" | sudo tee /etc/yum.repos.d/mongodb-org-4.0.repo

```
- Now, run the following command to install the MongoShell:
```
sudo yum install -y mongodb-org-shell

```
- Finally, we need to get the Mongoexport tools, so head over to:https://docs.mongodb.com/database-tools/installation/installation-linux/ and select the TGZ archive and follow the instructions.

## Step 7: Configure Security Groups to allow access to the DocumentDB cluster
- To allow our EC2 instance access to DocumentDB we will need to create a security group
- Head over to the VPC dashboard and select **Security Groups**
- Click **Create Security Group**
- We will name our security group "DocumentDB" and give it a description
- Now, we will add the following **Inbound Rule**: 

|Type|Protocol|Port Range|Source|Description|
|----|--------|----------|------|-----------|
|Custom TCP|TCP|27017|The Security Group of our EC2 instance|Allows Access to DocumentDB|

- Let's double check the **Outbound Security Group** for our EC2 instance and make sure it is as follows:

|Type|Protocol|Port Range|Source|Description|
|----|--------|----------|------|-----------|
|Custom TCP|TCP|27017|The Security Group of our DocumentDB cluster|Allows Access to DocumentDB|

- You now have SSH access to your DocumentDB cluster from your EC2 instance.

We have just completed Stage 2 (Setting Up DocumentDB). I know it toook a while but now we are ready to dive in and build our Lambda Function and populate our Database with some data! When you are ready, move on to the next stage.
