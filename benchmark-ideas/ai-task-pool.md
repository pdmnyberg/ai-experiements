Build a system with an agent pool which processes tasks from task queue.

Tasks should:
- should be able to specify tags that targets specific agents
- have an associated result storage so that output from a task can be collected
- be run by agents with tags that are a super set of the tags from the task
- be defined by a union of strictly defined task models for varying task types
  - the only initially required type should be BasicTask wich only includes a description

Agents should:
- allow configuration with different directives and models
- be tagged so that they can be matched to similarily tagged tasks
- be able to add tasks to the queue
- be able to list the available agents in the pool
- be considered unavailable when they have been assigned to a task
- not be stateful and the availability of the agent should be dictated by the pool

The system should:
- allow reading a JSON with initial tasks
- allow reading a JSON which specifies the available agents
- be built using python with type hints
- include example JSON files for both agents and tasks
- the execution should be considered parallell for a long as there are agents available
- the agent pool should be responsible for keeping the availability state of an agent
- the agent pool and the task queue should be separate subsystems
- the work should be performed by a runner or orchestrator that matches tasks with agents