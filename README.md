# Network Topology Monitoring Project

## Project Overview
The objective of this project is to establish a comprehensive live network topology monitoring system by collecting and analyzing log data from network elements, such as routers and switches. The focus will be on acquiring real-time insights into the dynamic relationships and configurations within the network infrastructure.

## Approach
The network topology is intricately structured into two primary layers: layer 3 (routing) and layer 2 (switching). Critical information, including the identification of neighboring nodes, service mappings, and overall network flow, is encapsulated in the routing tables of layer 3 devices, such as routers. To unveil these details, the project will leverage the collection and analysis of routing tables from layer 3 routing protocols, namely OSPF, ISIS, and BGP.

## Collection Phase
Routing Table Analysis
To accomplish live network topology monitoring, Python scripts have been meticulously crafted. These scripts are designed to gather routing tables from OSPF, ISIS, and BGP protocols. By extracting and consolidating data from these routing tables, the system will be able to discern the relationships between network nodes, providing a real-time snapshot of the network topology.

## ARP Table Examination
In addition to routing tables, the project will also focus on the ARP (Address Resolution Protocol) tables of edge devices. This information is vital for evaluating the connectivity of layer 2 devices within the network. By scrutinizing ARP tables, the system can ascertain the relationships and connectivity status of devices at the edge, contributing to a holistic understanding of the network topology.

## Conclusion
This network topology monitoring project aims to enhance visibility into the dynamic interactions within a network. Through meticulous data collection and analysis, the system will provide real-time insights into the relationships, configurations, and connectivity status of network elements. This proactive approach enables prompt identification and resolution of potential issues, ensuring the network operates seamlessly and efficiently.

 ## Lets get started

 [Guidance](guidance.md)

