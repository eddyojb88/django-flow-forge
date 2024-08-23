# Welcome to Django Flow Forge

The Data and ML Ops ecosystems are cluttered with overly complex solutions and vendor lock-ins that all carry significant pitfalls. Django Flow Forge aims to be a beacon of pragmatism when forging together your data ops and ML work flows.

## Designed for Data Scientists and Data Engineers
By building upon the Django frameowrk, a mature web server framework with modules that already solve a lot of problems in ML Ops, this plugin module aims to streamline tech stacks within these fields, focusing on standardization and flexibility as a project grows.

Django has a steeper learning curve than some other tools such as Luigi or Kedro, but as most data science projects grow, they typically end up requiring a production ready pipeline process and to serve the model in some way, leading you to despair as you had already invested in the tool that said would solve your problems.

Using this tool helps minimise the long term technical risk of most ml ops and data science projects.

![flow-forge-v0](https://github.com/eddyojb88/django-flow-forge/assets/22086433/7e3a81d7-ef98-4a99-96f7-f39d4f44ff9c)

## Features

- Define your pipelines as a series of tasks that are database backed and can run in sync or async (using Celery)
- Visualize your pipelines for stakeholders, both in planning and development phases (inspired by Kedro)
- Task monitoring and visualization of outputs and failures
- Compare data science experiment results easily (inspired by Kedro)
- Serve machine learning models efficiently
- A familiar environment for Django users, opening the door to a large developer community
- Leverage Django's robust security and scalability features, including Django Celery and flexbility to use Kubernetes engines, without the worry of vendor lock-in
- Encourages standardisation of data science work flows
- Encourages teams to move away from Jupyter Notebooks, which cause a plethora of issues

## Motivation

It is necessary in data science projects to:

- Design and keep track of data science projects in a way that can be easily communicated to team members and stakeholders
- Offer scalability when gathering data or model training in order to find (much) better solutions to complex problems

An ML system should also be simple enough that colleagues can:

(1) Find out when it isn’t working properly

(2) Make small changes to it

(3) Redeploy the model

In most cases, you dont need any of the highly specialised ML Ops tools out there. Our analysis revealed that in many cases, issues in machine learning operations can be attributed to bad code design and the use of notebooks.

### Inspiration

This package is inspired by the following articles that challenge the prevailing ML Ops narrative, drawing inspiration from critical discussions on the necessity and implementation of MLOps. This module seeks to avoid the pitfalls of overcomplication and excessive relaiance on overly specialized tools:

- [No, you dont need ML Ops](https://becominghuman.ai/no-you-dont-need-mlops-5e1ce9fdaa4b)
- [Do you need ML Ops](https://medium.com/@eddyojb/thoughts-you-wont-get-from-chatgpt-do-you-need-ml-ops-2c954b9d47a6)
- [I dont like Notebooks/Collab](https://www.youtube.com/watch?v=7jiPeIFXb6U)


### The State of the ML Ops ecosystem
The current MLOps landscape is cluttered with overengineered solutions. Analysis reveals a stark contrast in codebase size and functionality, with Django Flow Forge offering a lean yet powerful alternative to help solve end to end solutions (<4k of code vs Kedro with 430k lines of code!). Yet all other [tools analysed](https://medium.com/@eddyojb/thoughts-you-wont-get-from-chatgpt-do-you-need-ml-ops-2c954b9d47a6) have significant deficiencies. The features of Django Flow Forge are designed to meet a vision for a more accessible and flexible ML operational environment.

## Why not use e.g. Apache Beam?
Beam is great for realtime applications and massively scaling pipelines.  However, it isn't ideal for standardisation of data science workflows, monitoring and communicating or serving.
That said, there is no reason you cannot use Apache Beam within this package.