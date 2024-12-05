# Data Engineer Technical Test

## Context
The goals of this technical test are as follows:
- To allow us to see your technical level
- To try to determine your problem-solving skills
- To see if you can integrate into our technical team

## Deliverables
The minimum deliverables are as follows:
- A new public gitlab or github repo, which will contain an updated readme.md, the files you will write.
- A set of folders/files according to a clear nomenclature
- For each of the exercises, write the time it took you to complete it through a README that you will try to detail (markdown is recommended), preferably individually for each part

In the README, you should try to answer the following questions:
- What are the principles you applied
- Can you explain the decisions you made and why it is the best approach
- What are your recommendations for future work

## Exercice-1 : Onto-X Project
Let’s call the attached ontology “Onto-X”. Onto-X carries entities representing a hierarchy of
pathologies. Each entity is described by
- **Class Id**: representing a unique ID of the entity within the ontology
- **Preferred Label**: specifying the label of the entity
- **Parents**: representing one or more direct ancestors of the entity. The list of parents is
separated by a pipe “|”

### Tasks
The tasks is the following:
- Building a logical representation of Onto-X that preserves ancestor relationships (direct and indirect) and consequently enables reconstructing the hierarchy of entities. In other terms, for a given entity, we want to get all its relationships with the rest of the ontology entities. In addition we want to extract the depth of each relationship. For example: given the ID of “CERVIX DISORDER”, the API should return a dictionary of relationships:

```
    {
    “GYNECOLOGIC DISORDERS” : 2,
    “CERVIX DISORDERS”: 1,
    “CERVICITIS”: 0,
    “CERVIX NEOPLASM”, 0,
    “PAPANICOLAU SMEAR SUSPICIOUS”, 0
    “entity-X”: nx
    ,
    “entity-Y”: ny
    ,
    ......
    }
```
- The API should be implemented in python and should querybale through a Command Line Interface.

- Bonus #1: Expose the traetment via Rest API using FastAPI

- Bonus #2: Provide a Docker image of the RestAPI

## Exercise-2: DataViz
You'll find a sample KOL .pdf report in this repo.
This document begins with a preface containing a summary of the document, followed by a list of places and people classified by country.
You'll also find an .xlsx file containing the original data used to create the .pdf file.

### Tasks
- Create a stand-alone A4 document to add to the preface, containing a list of graphics summarizing the contents of the document.
- Use csv to create dataviz with real data.
- You can use any tool to create this A4 page, but you must deliver the code you use.

## Deadline and Evaluation

If you did not understand one of the instructions, you can contact me here: jeff@arcascience.ai

As a reminder, the test must be returned within 3 days maximum after receiving this email.Test commit
