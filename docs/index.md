# Welcome to Django Flow Forge

In a landscape cluttered with complex ML Ops solutions and vendor lock-ins that all carry significant pitfalls, Django Flow Forge aims to be a beacon of pragmatism when forging together your data science work flows.

## Designed for Data Scientists and Data Engineers
By relying on Django, a mature web server framework with modules that already solve a lot of problems in ML Ops, this plugin module aims to streamline tech stacks in Data or ML Ops *in the long run*, focusing on standardization and flexibility as a project grows, allowing it to be more impactful.

It has a more complex learning curve than other simple tools, but as most data science projects grow, they typically end up requiring a production ready pipeline process and to serve the model in some way, leading you back to a more complex tool like Django. The intelligent design here is that you learn how to use Django, rather than a plethora of other cobbled together tech, minimizing the long term technical risk of your projects.

![flow-forge-v0](https://github.com/eddyojb88/django-flow-forge/assets/22086433/7e3a81d7-ef98-4a99-96f7-f39d4f44ff9c)

## Features

- Easily define your data or ML flows (aka pipeline) as a DAG
- Visualize your flows for stakeholders, both in planning and development phases (inspired by Kedro)
- Simple pipeline registration and execution through a script, Django website or via an API by plugging in Django-ninja (Fast API for Django))
- Task monitoring and visualization of outputs and failures
- Visualise pipeline process outputs and failures for each task
- Compare data science experiment results easily (inspired by Kedro)
- Serve your models by plugging in Django Ninja
- A familiar environment for Django users, minimizing the learning curve
- Leverage Django's robust security
- Leverage Django's existing scalability features, including Django Celery and flexbility with Kubernetes engines, without the worry of vendor lock-in
- Encourages standardisation of data science work flows
- Encourages teams to move away from Notebooks, which cause a plethora of issues

## Motivation

It is necessary in data science projects to:

- Design and keep track of data science projects in a way that can be easily communicated to team members and stakeholders
- Offer scalability when gathering data or model training in order to find (much) better solutions to complex problems

An ML system should also be simple enough that colleagues can:

(1) Find out when it isn’t working properly

(2) Make small changes to it

(3) Redeploy the model

In most cases, you dont need any of the highly specialised ML Ops tools out there. Analysis reveals that in many cases, issues in, for example, machine learning operations can be attributed to bad code design and the use of notebooks.

### Inspiration

This package is inspired by the following articles that challenge the prevailing ML Ops narrative, drawing inspiration from critical discussions on the necessity and implementation of MLOps. This module seeks to avoid the pitfalls of overcomplication and excessive relaiance on overly specialized tools:

- [No, you dont need ML Ops](https://becominghuman.ai/no-you-dont-need-mlops-5e1ce9fdaa4b)
- [Do you need ML Ops](https://medium.com/@eddyojb/thoughts-you-wont-get-from-chatgpt-do-you-need-ml-ops-2c954b9d47a6)
- [I dont like Notebooks/Collab](https://www.youtube.com/watch?v=7jiPeIFXb6U)


### The State of the ML Ops ecosystem
The current MLOps landscape is cluttered with overengineered solutions. Analysis reveals a stark contrast in codebase size and functionality, with Django Flow Forge offering a lean yet powerful alternative to help solve end to end solutions (<4k of code vs Kedro with 430k lines of code!). Yet all other [tools analysed](https://medium.com/@eddyojb/thoughts-you-wont-get-from-chatgpt-do-you-need-ml-ops-2c954b9d47a6) have significant deficiencies. The features of Django Flow Forge are designed to meet a vision for a more accessible and flexible ML operational environment.

## Why not use e.g. Apache Beam?
Beam is fantastic for realtime applications and massively scaling pipelines.  However, it isn't ideal for standardisation of data science workflows, monitoring and communicating or serving.
That said, there is no reason you cannot use both. With flow-forge, you can define an Apache Beam pipeline with a Task if you require.