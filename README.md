# django_mlops

Ignore the ML Ops salesmen and get back to keeping your ML system simple, flexible and impactful with this handy plugin module for Django, aimed at Architects, Data Scientists and Data Engineers looking to save time by standardizing and simplifying their tech stack, not getting sucked in to development paralysis by vendor lock-in or tech stack complexity.

# Motivation

## Philosophy:

An ML system should be simple enough that an ops colleague can 

(1) Find out when it isn’t working properly

(2) Make small changes to it

(3) Redeploy the model

It is necessary in data science projects to:

- Design and keep track of data science projects in a way that can be communicated easily to team members and stakeholders easily
- Offer optional scalability in data ops or model training in order to find solutions to complex problems
  
## The State of the ML Ops ecosystem
It is highly questionable that any of the ML Ops tools, such as Kedro, KubeFlow, Metaflow or vendor solutions such as DataBricks etc. offer what is required to get your project done well, quickly and extensibly. They all appear to be packages with fancy webservers or a lot of bloat without solving the problem flexibly and robustly, which became the inspiration for Django ML Ops.

Lets quantify that statement e.g. the Kedro and Kedro-viz repos have about 430k lines of code. 80% of that is the react based viz and its assets but still, django_mlops has <3k lines of code and it is understood that it can achieve the same features and more.

## Key Features:
- Simple and mature framework with Django philosophy of robustness with safety and security
- Flexible in defining pipelines of tasks with or without a data science context
- Doesn't tie developers down to any scaling method - the repo includes an example with Celery and RabbbitMQ but it should also scale nicely to Kubernetes or any other package if required
- Visualization of DAGs, doubling up as a tool for stakeholder interactions (inspired by Kedro)

 ## Features to come
 - Implement better authentication and authorization options (at the moment you have to import the views in to urls and add login_required
 - Async capability: allow user to use the dependency tree in the graph in order to wait for relevant tasks that have been offloaded to complete
 - Make stakeholder only facing dashboard to display only tasks that succeeded


## Why Django and not Flask, FastAPI etc.
- Flask and FastAPI are great for starting out as they appear simple. However, every project that uses these tools ends up recreating logic that Django already has but badly and closed sourced. Why duplicate and add complexity?
- Django is realtively simple to deploy with Docker securely and scalably on any cloud service, keeping options flexible
- Django-ninja is FastAPI for Django, offering a fast way to serve models in a coupled or decoupled manner
- Move fast by starting off your project simple with django and decouple as and when you need. As you scale, your app in Django doesnt necessarily need to be rewritten

