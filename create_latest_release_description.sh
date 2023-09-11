#! /usr/bin/env sh

# Script that collects info about the latest release using a diff of the 2 latest tags
# and that outputs it as Markdown to be used as a GitLab release description.

LAST_TAGS=$(git for-each-ref --sort='-*committerdate' --count=2 --format '%(refname:short)' refs/tags)

CURRENT_TAG=$(echo "$LAST_TAGS" | head -n 1)

PREVIOUS_TAG=$(echo "$LAST_TAGS" | tail -n 1)

condition=$(echo "$LAST_TAGS" | wc -l);[ $condition -le 1 ] && PREVIOUS_TAG=$(git rev-list --max-parents=0 HEAD)

printf "# Changes\n\n"

./extract_changelog.py "$CURRENT_TAG"

printf "\n## Commits since the last version\n\n"

printf "<details><summary>Click to expand</summary>\n\n"

git --no-pager log --pretty="- [%as] %h %s" --no-merges --reverse ${PREVIOUS_TAG}..${CURRENT_TAG}

printf "\n</details>"
