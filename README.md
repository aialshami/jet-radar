![jet banner](https://i.ibb.co/R0YkPvk/private-jet-in-the-sun-banner-tcm36-53924-overlay.png)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#introduction">Introduction</a>
      <ul>
        <li><a href="#our-purpose">Our Purpose</a></li>
        <li><a href="#features">Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#who-are-we-tracking">Who Are We Tracking?</a></li>
        <li><a href="#the-dashboard">The Dashboard</a></li>
      </ul>
    </li>
    <li><a href="#adsb-exchange">ADS-B Exchange API</a></li>
    <li>
      <a href="#the-architecture">The Architecture</a>
      <ul>
        <li><a href="#aws-services">AWS Services</a></li>
        <li><a href="#database-schema">Database Schema</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#licenses">Licenses</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>
<break>
</break>

## Introduction

Welcome to JET-RADAR! This repository houses a data collection and visualisation system that utilizes the ADS-B Exchange API to gather live data from private aircraft. By creating a robust pipeline and leveraging the Dash framework, JET-RADAR allows you to store, analyze, and visualize real-time data related to aircraft, their owners and ultimately... their environmental impact.

### Our Purpose

At JET-RADAR, our purpose is to raise awareness about the carbon emissions generated by the rich and powerful through their extensive use of private jets. By providing detailed insights into the movements of celebrity jets, we aim to highlight the environmental impact of excessive air travel and encourage sustainable alternatives. Our platform serves as a valuable resource for media professionals, advocates of stricter legislation against private air travel, and environmental advocates, enabling them to access accurate data and make informed arguments for change. Together, we can promote responsible aviation practices, advocate for stricter legislature, and work towards a greener future.

### Features

- Real-time data collection from the ADS-B Exchange API.
- Storage of collected data in a database for historical analysis.
- Interactive visualisations powered by Dash to explore aircraft movements and emission statistics with a 24 hour delay.
- Customizable filters and search options to narrow down specific private aircraft owners.
- Integration with AWS services for a scalable and reliable architecture.

## Getting Started

To view our live Dashboard please click on the image below:

[![airplane door](https://twistedsifter.com/wp-content/uploads/2022/01/Screen-Shot-2022-01-06-at-8.33.44-AM.png?w=1024)](https://www.youtube.com/watch?v=xvFZjo5PgG0)

Want to launch your own JET-RADAR data collection and visualisation system? Or do you want to contribute to the project? Follow the guidelines in the next sections to get started:

### Prerequisites

Before you begin, ensure that you have the following prerequisites installed:

- <a href="https://www.terraform.io/downloads.html"><img src="https://www.svgrepo.com/show/354447/terraform-icon.svg" height="20" alt="Terraform Logo"></a> Terraform (version 1.2.0 or above)

- <a href="https://www.python.org/downloads/"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" height="20" alt="Python Logo"></a> Python (version 3.10 or above)

- Pip (a package installer for Python)

### Installation

To install and set up JET-RADAR, follow these steps:

1.  Fork the repository by clicking: <a href="https://github.com/aialshami/jet-radar/fork"><img src="https://upload.wikimedia.org/wikipedia/commons/3/38/GitHub_Fork_Button.png" height="20" alt="Python Logo"></a>

    This will create a copy of the repository under your GitHub account.

2.  In your forked repository, navigate to the "Settings" tab and click on "Secrets" in the left sidebar. Click on the "New repository secret" button.

3.  Create a secret key-value pair for each of the following variables:

    - `ACCESS_KEY`: Your AWS access key.
    - `SECRET_KEY`: Your AWS secret key.
    - `RAPIDAPI_KEY`: Your RapidAPI key.
    - `DB_PASSWORD`: Password for the database.

    **Note**: Ensure the secret keys are properly secured and not exposed publicly.

4.  Still in the "Settings" tab, click on "Environment" in the left sidebar. Click on the "New environment" button.

5.  Create an environment called `jet_env` and add the following variables:

    - `CELEB_INFO`: `celeb_planes.json`.
    - `DB_HOST`: Hostname or endpoint of your database server.
    - `DB_NAME`: Name of the database.
    - `DB_PORT`: Port number for database connection.
    - `DB_USER`: Username for the database.
    - `PRODUCTION_SCHEMA`: `production`.
    - `RAPIDAPI_HOST`: `adsbexchange-com1.p.rapidapi.com`.
    - `S3_BUCKET_NAME`: `jet-bucket`.
    - `STAGING_SCHEMA`: `staging`.
    - `STAGING_TABLE_NAME`: `tracked_event`.

6.  In your forked repository, run the deploy workflow by first, going into the action tab then activating workflows. This utilizes Terraform to create the AWS services required by the application. This action will provision the necessary infrastructure for data collection and storage.

7.  Clone your forked repository to your local machine:

    ```bash
    git clone https://github.com/your-username/jet-radar.git
    ```

8.  Change into the dashboard directory:

    ```bash
    cd jet-radar/dashboard
    ```

9.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

10. Start the application:

    ```bash
    python app.py
    ```

    Access the JET-RADAR dashboard by opening a web browser and navigating to the provided link (e.g. **http://localhost:8080**). You should now see the dashboard and be able to interact with it locally.

    If you prefer, you can also deploy the JET-RADAR repository onto the EC2 instance built through terraform or any other hosting platform of your choice.

    1. Launch an EC2 instance on AWS and connect to it using SSH.

    2. Install Git on the EC2 instance. Run the following command:

    ```bash
    sudo apt-get update
    sudo apt-get install git
    ```

    3. Clone your forked repository onto the EC2 instance. Replace your-username and your-repo with your GitHub username and repository name respectively:

    ```bash
    git clone https://github.com/your-username/jet-radar.git
    ```

    4. Change into the cloned repository directory:

    ```bash
    cd jet-radar
    ```

    5. Install the required dependencies. Make sure you have Python and Pip installed on the EC2 instance. Run the following command:

    ```bash
    pip install -r requirements.txt
    ```

    6. Set up the necessary environment variables. You can either export the variables directly on the EC2 instance or create a .env file and populate it with the required variables.

    7. Start the application:

    ```bash
    python app.py
    ```

    The JET-RADAR dashboard should now be accessible by opening a web browser and navigating to the provided IP address or domain name of your EC2 instance, along with the appropriate port (e.g., **http://your-ec2-ip-address:8080**).

    Remember to configure security groups and network settings for your EC2 instance to allow inbound traffic on the required port.

    Please note that these instructions assume a basic familiarity with AWS EC2 instances and SSH connections. Make sure to adjust the instructions as per your specific setup and requirements.

## Usage

### Who Are We Tracking?

JET-RADAR tracks the private jet movements of various celebrities and influential individuals. Here are the notable personalities being monitored:

- Elon Musk
- Tom Cruise
- Oprah Winfrey
- Floyd Mayweather
- Taylor Swift
- Bill Gates
- Kim Kardashian
- Travis Scott
- Kylie Jenner
- Donald Trump
- Jim Carrey
- John Travolta
- Jay-Z
- Steven Spielberg
- Mark Wahlberg
- A-rod

By utilizing the ADS-B Exchange API and real-time data collection, JET-RADAR provides up-to-date information on the flight paths and locations of these private aircraft.

### The Dashboard

## ADS-B Exchange API

JET-RADAR utilizes the [**ADS-B Exchange API**](https://rapidapi.com/adsbx/api/adsbexchange-com1) to collect real-time data on private aircraft movements. This comprehensive API provides information on aircraft positions, flight numbers, and more. By integrating the ADS-B Exchange API, JET-RADAR ensures accurate and up-to-date data on private jet movements. With the ADS-B Exchange API, JET-RADAR offers a reliable platform for tracking and recording unsustainable aviation practices.

## The Architecture

### AWS Services

![data architecture](https://i.ibb.co/ZNSq37D/image-2.png)

1. ECR (Elastic Container Registry): JET-RADAR utilizes two ECR repositories. The staging ECR holds a dockerised image of the extract application. This application extracts data from the ADS-B Exchange API and stores it in a staging schema in an RDS (Relational Database Service). The production ECR contains a dockerised image of the transform application, which cleans the data and calculates metrics such as fuel usage.

2. Lambda: The extract application is deployed as a Lambda function and triggered by EventBridge every 10 minutes. This ensures regular extraction of data from the ADS-B Exchange API and storage in the staging schema. The transform application is also deployed as a Lambda function, triggered by EventBridge to run every 24 hours. This periodic execution allows for data cleaning and metric calculations and is in consideration of the aircraft user's safety.

3. RDS (Relational Database Service): JET-RADAR utilizes an RDS instance with two schemas. The staging schema stores the extracted data from the ADS-B Exchange API, serving as an intermediate storage for the raw data before the transformation process. The production schema holds the transformed and processed data, which is ready for consumption by the dashboard server.

4. S3 (Simple Storage Service): JET-RADAR utilizes an S3 bucket to store the documentation required for the extract application. This bucket holds the necessary resources for extracting and processing data from the ADS-B Exchange API.

5. EventBridge: EventBridge acts as a central event bus that triggers the extract and transform Lambda functions. It enables scheduling and orchestrating the periodic execution of these functions at specific intervals. With EventBridge, JET-RADAR ensures the timely and automated execution of data extraction and transformation processes.

6. EC2 Instance and Load Balancer: The dashboard server, responsible for visualizing the data, is hosted on an EC2 instance. A load balancer ensures scalability and high availability of the dashboard. The dashboard server pulls data from the production schema in the RDS, where the transformed and processed data is stored.

### Database Schema

JET-RADAR utilizes two distinct database schemas: the staging schema and the production schema. These schemas are designed to efficiently store and manage the extracted and transformed data from the ADS-B Exchange API.

**Staging Schema**:
The staging schema represents an unnormalised structure with a single table that holds the raw extracted data. This schema serves as an intermediate storage for the data before it undergoes the transformation process. Here is an image representing the structure of the staging schema:

![staging erd](https://i.ibb.co/wsC6KgH/draw-SQL-staging-export-2023-05-17.png)

**Production Schema**:
The production schema employs a normalised structure to store the transformed and processed data. It consists of 11 tables that are organized to the 3rd degree of normalisation, ensuring data integrity and reducing redundancy. The tables in the production schema are designed to efficiently store and query the data for visualization and analysis. Here is an image illustrating the structure of the production schema:

![production erd](https://i.ibb.co/hBFhq2c/draw-SQL-production-export-2023-05-25.png)

By utilizing these two schemas, JET-RADAR effectively manages the data flow from extraction to transformation and provides a well-organized structure for storing and retrieving the processed data.

## Roadmap

### Phase 1: Historical Data and International Access

**Objective**: Enable access to historical data and expand coverage to planes registered outside the US.

**Tasks**:

- Research and identify reliable sources of historical aviation data.
- Implement data retrieval and storage mechanisms for historical data.
- Enhance data collection processes to include planes registered outside the US.

### Phase 2: Cost of Fuel Conversion

**Objective**: Automate the conversion of fuel costs for enhanced analysis.

**Tasks**:

- Integrate with relevant fuel cost APIs or data sources.
- Develop algorithms to convert and normalize fuel cost data.
- Implement automated data processing to incorporate fuel cost conversion.

### Phase 3: Custom Domain and Social Media Integration

**Objective**: Host the dashboard on a custom domain and integrate with social media platforms.

**Tasks**:

- Register a custom domain and set up hosting infrastructure.
- Configure the dashboard to be accessible via the custom domain.
- Implement social media integration with platforms like Twitter and Facebook.

### Phase 4: User Contributions

**Objective**: Allow users to contribute private jet owners to the catalogue.

**Tasks**:

- Develop user registration and authentication mechanisms.
- Implement a submission process for users to contribute private jet owner details.
- Establish moderation and verification processes for user-contributed data.

### Phase 5: Daily Reports and Automation

**Objective**: Provide daily reports to subscribers and automate the process.

**Tasks**:

- Design and develop report generation functionality.
- Implement a scheduling mechanism for automatic report generation.
- Configure email delivery system to send reports to subscribers.

## Third-Party Services and Software

<a href="https://aws.amazon.com/service-terms/"><img src="https://static-00.iconduck.com/assets.00/aws-icon-1024x1024-xh5ti9kd.png" height="100" alt="AWS Logo"></a>
<a href="https://www.docker.com/legal/docker-terms-service/"><img src="https://www.docker.com/wp-content/uploads/2022/03/vertical-logo-monochromatic.png" height="100" alt="Docker Logo"></a>
<a href="https://rapidapi.com/terms/"><img src="https://rapidapi.com/static-assets/default/favicon-8e7d522e-653f-4edd-ac27-3f6ed950e45d.png" height="100" alt="Rapidapi Logo"></a>
<a href="https://docs.github.com/en/site-policy/github-terms/github-terms-of-service"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/2048px-Octicons-mark-github.svg.png" height="100" alt="Github Logo"></a>
<a href="https://registry.terraform.io/terms"><img src="https://www.svgrepo.com/show/354447/terraform-icon.svg" height="100" alt="Terraform Logo"></a>
