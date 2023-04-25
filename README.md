# CLIP - Search Engine - Text Requests to Images
> Made as the project of **Case Study** Module from the Engineer Path of CY TECH.

<br>

It is a project based on the connection between text and images using [CLIP](https://openai.com/research/clip). We realized the project using [Python](https://www.python.org/), [Fiftyone](https://docs.voxel51.com/), [Pinecone](https://pinecone.io) and [Streamlit](https://streamlit.io/). The project is deployable through [Docker](https://www.docker.com/).
We describe the project with the following sections.
- [I. Project Demonstration](#project-demonstration)
- [II. Repository Structure](#repository-structure)
- [III. Project Description](#project-description)
- [IV. Project Deployment](#project-deployment)
    - [Online Deployment](#online-deployment)
    - [Local Deployment](#local-deployment)


## I. Project Demonstration
<img src="./src/static/gif/Demonstration.gif"/>

<br>

## II. Repository Structure
The structure of this repository is described below. It contains the source code of the project as well as the Dockerfile used to build the Docker Image.

```bash
├── app.py  
├── Dockerfile  
├── requirements.txt    
└── src    
    ├── embedding.py  
    ├── fiftyone_datasets_models.py  
    ├── static    
    │   └── images  
    │       └── iconCYTECH.png  
    └── utils.py
```
<br>

## III. Project Description

In the recent years, AI has been improving quite a lot. The purpose of this project is to demonstrate the power of existing Computer Vision Model (CLIP from OpenAI) to build a Search Engine. The Search Engine is based on the connection between text and images. Thus, the user can type a text and the Search Engine will return the most relevant images based on the text.

To realize this project, we used the following tools.
- Fiftyone
- Pinecone
- Streamlit
- Docker

<br>


## IV. Project Deployment

### Online Deployment

The interface is hosted through Streamlit. It is available at the following [Link](https://dorian-roux-clip-case-study-app-c97l2x.streamlit.app/).

<br>

### Local Deployment

The local deployment is based on Docker. Thus, to correctly launch our interface, the [Docker](https://www.docker.com/) software must be installed. The deployment is relatively easy since it consists of the three steps described below.

#### **1° - Clone the Repository**
Firstly, you must clone this reposity. To do so, you can use the following command.
```bash
git clone https://github.com/dorian-roux/Clip-Search-Engine
```

#### **2° - Obtain the Pinecone Key Parameters**
Secondly, you must create a find your Picone Key parameters. To do so, you need to register in their [website](https://pinecone.io). Then you need to find the [Pinecone Console](https://app.pinecone.io/organizations) and keep both the **Pinecone Key Value** and **Pinecone Key Environement**


#### **3° [Recommended] - Modify the State within the Dockerfile**
To prevent the modification on the deployed application, we define within the Dockerfile, a boolean `DISABLE_CONFIG_BUTTONS` which is set to True. If you wish to try multiple configurations within the app, you must modify the following line:
```bash
RUN echo 'DISABLE_CONFIG_BUTTONS = True' > /app/config.py
```
by this next line:
```bash
RUN echo 'DISABLE_CONFIG_BUTTONS = False' > /app/config.py
```

#### **4° - Build the Docker Image**
Thirdly, you need to build the Docker Image based on this repository Dockerfile. To do so, you can use the following command.
```bash
docker build -t {TAG} .
```
<u>Note:</u> &nbsp; `{TAG}` is the name you want to give to your Docker Image. It is used to identify it later.


#### **5° - Run the Docker Container**
Finally, you need to run the Docker Container based on the Docker Image you just built. To do so, you can use the following command.
```bash
docker run -p 8501:8501 {TAG}
```
<u>Note:</u> &nbsp; We defined the port `8501` as the port used by the Streamlit Interface. Thus, you can access it by typing `localhost:8501` in your browser.



