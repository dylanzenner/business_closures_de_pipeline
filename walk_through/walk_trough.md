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

