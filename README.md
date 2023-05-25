![jet banner](https://aircharterservice-globalcontent-live.cphostaccess.com/images/blog-images/private_jet_in_the_sun_banner_tcm36-53924.jpg)

# JET-RADAR ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️ ✈️

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

## Introduction 🌍✈️

Welcome to JET-RADAR! This repository houses a data collection and visualisation system that utilizes the ADS-B Exchange API to gather live data from private aircraft. By creating a robust pipeline and leveraging the Dash framework, JET-RADAR allows you to store, analyze, and visualize real-time data related to aircraft, their owners and ultimately... their environmental impact.

### Our Purpose

At JET-RADAR, our purpose is to raise awareness about the carbon emissions generated by the rich and powerful through their extensive use of private jets. By providing detailed insights into the movements of celebrity jets, we aim to highlight the environmental impact of excessive air travel and encourage sustainable alternatives. Our platform serves as a valuable resource for media professionals, advocates of stricter legislation against private air travel, and environmental advocates, enabling them to access accurate data and make informed arguments for change. Together, we can promote responsible aviation practices, advocate for stricter legislature, and work towards a greener future. ♻️🌎

### Features

- Real-time data collection from the ADS-B Exchange API.
- Storage of collected data in a database for historical analysis.
- Interactive visualizations powered by Dash to explore aircraft movements and emission statistics.
- Customizable filters and search options to narrow down specific private aircraft owners.
- Integration with AWS services for a scalable and reliable architecture.

## Getting Started

To view our live Dashboard please click on the image below 👇:

[![airplane door](https://twistedsifter.com/wp-content/uploads/2022/01/Screen-Shot-2022-01-06-at-8.33.44-AM.png?w=1024)](https://www.youtube.com/watch?v=xvFZjo5PgG0)

Want to launch your own JET-RADAR data collection and visualisation system? Or do you want to contribute to the project? Follow the guidelines in the next sections to get started👇:

### Prerequisites

Before you begin, ensure that you have the following prerequisites installed:

- Terraform (version 1.2.0 or above) <a href="https://www.terraform.io/downloads.html"><img src="https://blogs.vmware.com/cloudprovider/files/2019/04/og-image-8b3e4f7d-blog-aspect-ratio.png" height="20" alt="Python Logo"></a> <-- click to download

- Python (version 3.10 or above) <a href="https://www.python.org/downloads/"><img src="https://www.python.org/static/community_logos/python-logo-generic.svg" height="20" alt="Python Logo"></a> <-- click to download

- Pip (a package installer for Python)

### Installation

To install and set up JET-RADAR, follow these steps:

1. Clone the repository:

   ```bash
   git fork https://github.com/aialshami/JET-RADAR.git
   ```

   ```bash
   cd JET-RADAR
   ```

   ```bash
    cd
   ```

   add environment variables to github
   run deploy action
   cd into
