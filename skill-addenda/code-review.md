## Local amendments

These amendments come from the local skill build and take precedence over the steps above where they conflict.

### PR targets

When the fixed point is a PR number (`#85`), `HEAD` is the local checkout, not the PR. Run `gh pr view <n> --json baseRefName,headRefName,body`, fetch both branches, and use `git diff origin/<base>...origin/<head>` and `git log origin/<base>..origin/<head>` in place of the `HEAD` forms in step 1. Sub-agents read full files at the PR head with `git show origin/<head>:<path>`.

For the spec source, closing keywords in the PR body (`Closes #81`) come first, ahead of commit messages.

### Shared standards

Step 3's sources always include the **Coding Style & Engineering Principles** section at the end of this file: paste it into the Standards sub-agent prompt beside the repo's own sources. Where a repo documents a conflicting rule, the repo wins.

### Runtime configuration

When the diff changes runtime configuration (web server or proxy config, Compose files, Dockerfiles, CI workflows), the diff alone hides how requests actually behave. Add to the Spec sub-agent brief: run the changed configuration in an isolated environment (a detached git worktree, uniquely named containers and networks, a free host port), remove everything it creates, and label each finding as verified by running or by reading.

<!-- INCLUDE:shared/coding-style.md -->
