---
name: vibeflow:increment
description: Start incremental requirements development for an existing VibeFlow project.
disable-model-invocation: true
---

To start an increment cycle:

1. Create `.vibeflow/increment-request.json` in project root with the reason and scope:
   ```json
   {
     "reason": "Brief description of why new requirements are needed",
     "scope": "Brief scope of changes"
   }
   ```
2. The router will detect this file and route to the increment phase
3. After processing, the signal file is removed and the router re-evaluates the phase
