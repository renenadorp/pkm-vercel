# Database 



| Command                             | Effect                                         |     |
| ----------------------------------- | ---------------------------------------------- | --- |
| `match (a) -[r] -> () delete a, r`  | Delete all nodes with relations                |     |
| `match (a) delete a`                | Delete nodes without relations                 |     |
| `CREATE OR REPLACE DATABASE <name>` | Clear an existing database or create a new one |     |


# Create Nodes - Using Neo4j Desktop

## From CSV
- Make sure to update the neo4j settings for the import folder (comment out).
- 
**Command**:
`LOAD CSV WITH HEADERS FROM 'file:////Users/rnadorp/Documents/Prive/neo4j/UseCases.csv' AS row FIELDTERMINATOR ';' CREATE (u:UseCase{name: row.Name}) RETURN row.Id, row.Name, row.Descr; ` 

Make sure to include the <p style="display: inline; color:red;">CREATE </p> clause, otherwise neo4j will not create any labels. 

# Create Relationships


# Show Data

| Command                             | Effect                                         |
| ----------------------------------- | ---------------------------------------------- | 
| `MATCH (n) RETURN n; ` | Show all data   |



# Batch Script
```
// clear data
MATCH (n)
DETACH DELETE n;

// load UseCase nodes
LOAD CSV WITH HEADERS FROM 'file:////Users/rnadorp/Documents/Prive/neo4j/UseCases.csv' AS row 
WITH row WHERE row.Id IS NOT NULL
FIELDTERMINATOR ';' 
CREATE (u:UseCase{Id: row.Id, name: row.Name}) 
RETURN count(u);


LOAD CSV WITH HEADERS FROM 'file:////Users/rnadorp/Documents/Prive/neo4j/Propositions.csv' AS row
MERGE (p:Proposition {Id: row.Id, name: row.Name})
RETURN count(p);


// create relationships
LOAD CSV WITH HEADERS FROM 'file:////Users/rnadorp/Documents/Prive/neo4j/Relation_UseCase_Proposition.csv' AS row
MATCH (u:UseCase {UseCaseId: row.UseCaseId})
MATCH (p:Proposition {PropositionId: row.PropositionId})
MERGE (p)-[:IS_TARGETING]->(u)
RETURN *;

```
