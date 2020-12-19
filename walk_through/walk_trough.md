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
