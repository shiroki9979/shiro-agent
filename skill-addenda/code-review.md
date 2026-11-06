## Local amendments

These amendments come from the local skill build and take precedence over the steps above where they conflict.

### PR targets

When the fixed point is a PR number (`#85`), `HEAD` is the local checkout, not the PR. Run `gh pr view <n> --json baseRefName,headRefName,body`, fetch both branches, and use `git diff origin/<base>...origin/<head>` and `git log origin/<base>..origin/<head>` in place of the `HEAD` forms in step 1. Sub-agents read full files at the PR head with `git show origin/<head>:<path>`.

For the spec source, closing keywords in the PR body (`Closes #81`) come first, ahead of commit messages.

### Shared standards

Step 3's sources always include the **Coding Style & Engineering Principles** section at the end of this file: paste it into the Standards sub-agent prompt beside the repo's own sources. Where a repo documents a conflicting rule, the repo wins.

### Runtime configuration

When the diff changes runtime configuration (web server or proxy config, Compose files, Dockerfiles, CI workflows), the diff alone hides how requests actually behave. Add to the Spec sub-agent brief: run the changed configuration in an isolated environment (a detached git worktree, uniquely named containers and networks, a free host port), remove everything it creates, and label each finding as verified by running or by reading.

### Stale fixed point

A local branch used as the fixed point may be behind its upstream (the user merged `origin/master` into the feature branch, but never fast-forwarded local `master`). Then the three-dot merge-base is the old local tip, and the diff absorbs every upstream change that merge brought in. In step 1, before the resolve check:

1. Run `git fetch` once. If it fails (offline), keep the fixed point as given and say in the report that the upstream comparison was skipped.
2. If the fixed point is a local branch with an upstream (`git rev-parse --abbrev-ref <fixed-point>@{u}` succeeds), count both directions: `behind = git rev-list --count <fixed-point>..<fixed-point>@{u}`, `ahead = git rev-list --count <fixed-point>@{u}..<fixed-point>`.
3. `behind > 0` and `ahead == 0`: use `<fixed-point>@{u}` instead, in both the diff and the log command, and open the report with one line naming the substitution and the commit count.
4. `behind > 0` and `ahead > 0`: the branches diverged. Stop and ask the user which ref to review against; don't pick one.
5. Otherwise use the fixed point as given.

### Spec sub-agent test scope

The Spec axis reads code against the spec; it isn't a regression run. Add to the Spec sub-agent brief: don't run the test suite. Run a single test file only when one finding needs an execution result as evidence, and label that finding as verified by running. The full suite's result comes from the issue's acceptance record, and the main thread doesn't rerun it either. The Runtime configuration amendment above still applies as written.

<!-- INCLUDE:shared/coding-style.md -->
