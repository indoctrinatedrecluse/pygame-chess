#!/bin/bash

# This script automates the release process.
# It reads the latest version from CHANGELOG.md, commits any outstanding changes,
# tags the commit, and pushes to the remote to trigger the release workflow.

# 1. Get the latest version from the CHANGELOG
# This command uses grep and sed to find the first line like '## [v1.0.0]' and extract the version.
LATEST_VERSION=$(grep -m 1 -o -E "^## \[(v[0-9]+\.[0-9]+\.[0-9]+)\]" CHANGELOG.md | sed -E 's/## \[(v[0-9]+\.[0-9]+\.[0-9]+)\]/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Could not find a version string like '## [v1.0.0]' in CHANGELOG.md"
    exit 1
fi

echo "Latest version found: $LATEST_VERSION"

# 2. Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes found. Committing..."
    git add .
    git commit -m "Release $LATEST_VERSION"
    if [ $? -ne 0 ]; then
        echo "Git commit failed. Please resolve the issues and try again."
        exit 1
    fi
else
    echo "No uncommitted changes."
fi

# 3. Create a git tag with the version number
# Use -f to force update the tag if it exists locally.
echo "Creating git tag: $LATEST_VERSION"
git tag -f "$LATEST_VERSION"

# 4. Push the commit and the tag to the 'master' branch
echo "Pushing commit and tag to origin/master..."
git push origin master
git push origin "$LATEST_VERSION"

echo "Push complete. The GitHub Actions release workflow should now be triggered."
