# Agent Instructions

## Thorough Investigation

Before reporting back to the user, ensure you have thoroughly investigated the issue. This includes:

- [ ] **Reproducing the issue:** If possible, try to reproduce the issue yourself. This will help you to understand the problem better.
- [ ] **Checking the logs:** Always check the logs for any error messages or other relevant information.
- [ ] **Consulting the documentation:** If the issue is related to a specific library or API, consult the documentation to see if there is any information that could help.
- [ ] **Searching for similar issues:** Search online for similar issues that other people may have had. This can often lead to a quick solution.
- [ ] **Considering multiple solutions:** Don't just settle for the first solution that comes to mind. Consider multiple solutions and choose the one that is the most robust and maintainable.
- [ ] **Explaining the root cause:** When you do report back to the user, make sure to explain the root cause of the issue and how you fixed it. This will help the user to understand the problem and avoid it in the future.

## Coding Standards

- Use full words for names. Do not use abbreviations.
- Do not use one-letter variable names.
- Do not add comments. Use well-named classes, functions, methods, and variables instead.
- If code needs explanation, factor it into clearer names or smaller functions.
- Use type annotations for project code.
- Keep `pyright` passing.
- Treat ORM and framework APIs as typed boundaries. Do not refactor SQLAlchemy models only to satisfy the type checker.
- Use narrow annotations, casts, or `Any` at framework boundaries when strict typing would otherwise require it.

## Server Management

- To start the server, use the command `g-dev start`. Returns immediately after starting in background. Do not wait for it.
- To stop the server, use the command `g-dev stop`. Returns immediately. Do not wait for it.
- To restart the server, use the command `g-dev restart`. Returns immediately. Do not wait for it.
- To check the status of the server, use the command `g-dev status`.
- To see the server logs, use the command `g-dev logs`.

## Windows Setup

The project uses Nix flakes and direnv on Linux/macOS. On Windows, equivalent PowerShell scripts are provided:

- `setup-env.ps1` — creates a `.venv`, installs Python dependencies, sets `FLASK_APP=app`, and sources `.env` files.
- `.envrc.ps1` — auto-activates the environment when entering the project directory (add to `$PROFILE`).

Run `.\setup-env.ps1 -Install` once to bootstrap the environment.

## Workflow

- After making **any** code change, you **must** immediately restart the server using `g-dev restart`. Do not skip this step.
- Once the server is restarted, verify it started successfully before reporting to the user.
- If the server fails to start, check the logs with `g-dev logs` and fix the issue.
- Do not ask for permission to proceed with a plan if in build mode. Execute the plan directly.
