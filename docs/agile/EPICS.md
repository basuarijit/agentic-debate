# Epics

Source: `Requirements Document for a Debate application.docx`

## Epic E1: Automated Debate Orchestration

Enable the application to run a complete debate process automatically using AI agents.

### Business Value

Users can initiate or observe a structured debate without manually coordinating the debate flow.

### BRD Traceability

- "This will be an application for a debate process"
- "Every debate will be executed automatically by AI agents"

## Epic E2: Debate Topic Selection

Provide a debate-topic-selector agent that selects the debate topic and starts the debate.

### Business Value

The system can autonomously define what the debate is about, making each debate executable without manual topic setup.

### BRD Traceability

- "A topic of the debate will be selected by a debate-topic-selector agent."
- "This agent will select a topic and initiate the debate."

## Epic E3: Opposing Argument Agents

Provide two debate agents: one arguing in favor of the selected topic and one arguing against it.

### Business Value

The debate has balanced representation from both sides of the selected topic.

### BRD Traceability

- "There will be two other agents in the process."
- "One agent will argue in favor of the topic."
- "The other agent will argue against the topic."

## Epic E4: Debate Turn Management

Control the debate sequence so each argument agent speaks exactly three times, with the starting side chosen randomly.

### Business Value

The debate follows a predictable and fair structure while still allowing variation in which side starts.

### BRD Traceability

- "Each agent will get to speak 3 times."
- "The debate-topic-selector agent will select the topic and randomly start with one of the two arguing agents."

## Epic E5: Debate Judging

Provide a judge agent that evaluates the completed debate and decides the winner.

### Business Value

Each debate produces a clear outcome after both sides have presented their arguments.

### BRD Traceability

- "There will be a fourth agent called the judge agent who will decide the winner of the debate."

## Epic E6: Backend And Frontend Application Structure

Deliver the application as separate backend and frontend components.

### Business Value

The solution can evolve with clear separation between API/agent orchestration responsibilities and user interface responsibilities.

### BRD Traceability

- "The application will be divided into backend and frontend."

