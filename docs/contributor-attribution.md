# Contributor attribution preflight

Accurate commit metadata helps reviewers trace changes to contributors. Run these checks inside the working repository before committing. They check attribution, not proof of authorship or code safety.

## 1. Check the effective identity

```sh
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
git config --show-origin --get user.name
git config --show-origin --get user.email
```

The first two commands show the identities Git would use in the current command environment. The configuration queries locate the configured values; a missing value returns a nonzero exit status. Environment variables, command-line options and editor integrations can override configuration, so inspect the resulting commit too. See [git-var](https://git-scm.com/docs/git-var) and [git-config](https://git-scm.com/docs/git-config).

If a repository needs a different identity, replace both placeholders before running:

```sh
git config --local user.name "YOUR NAME"
git config --local user.email "YOUR GITHUB-LINKED EMAIL"
```

Use an email associated with your GitHub account, or copy your exact GitHub-provided noreply address from your email settings. Do not construct an address from a username. Repository-local settings leave other repositories unchanged and affect future commits, not existing history. See [setting your commit email address](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address).

A successful push authenticates access; it does not establish that the stored author email belongs to the intended account. Generic addresses such as `contributor@computer.local` cannot be linked to GitHub accounts. See [troubleshooting missing contributions](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions).

## 2. Credit actual shared work

Agree on each contributor's contribution and preferred attribution address. For a jointly authored commit, add one `Co-authored-by` trailer per co-author, separated from the description by a blank line. Example commit message, with fictional placeholders:

```text
docs: clarify the local validation workflow

Explain the checks and how to interpret their results.

Co-authored-by: COLLABORATOR NAME <COLLABORATOR EMAIL>
```

Replace the placeholders with the collaborator's chosen name and GitHub-linked email. Ask for their GitHub-provided noreply address if they want email privacy. Commit metadata is published when pushed to this public repository. Attribute the work actually included; a review request alone is not a co-authored contribution. See [GitHub's co-author instructions](https://docs.github.com/en/pull-requests/how-tos/commit-changes/creating-a-commit-with-multiple-authors).

## 3. Inspect the original commit

After committing and before pushing:

```sh
git log -1 --format='commit %H%nAuthor: %an <%ae>%nCommitter: %cn <%ce>%n%n%B'
git show -s --format=%B HEAD | git interpret-trailers --parse
```

Check the raw author and committer fields, description and co-author trailers. For multiple new commits, repeat with each commit SHA instead of `HEAD`; the first command can take the SHA as its final argument. Do not copy private email output into a public issue or PR.

After pushing, open the PR's **Commits** tab and inspect each original commit's linked authors. Inspect the resulting merge or squash commit separately: it is not evidence that the original commits had the same attribution. Local checks cannot confirm GitHub account association or achievement eligibility.

If attribution is wrong, stop before merging and discuss the correction with the contributors and maintainer. Updating local configuration does not repair old commits. Do not rewrite shared history or replay merged work solely to alter contribution counts.

See [git-log formatting](https://git-scm.com/docs/pretty-formats) and [git-interpret-trailers](https://git-scm.com/docs/git-interpret-trailers).
