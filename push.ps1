# This script automates the release process.
# It reads the latest version from CHANGELOG.md, commits any outstanding changes,
# tags the commit, and pushes to the remote to trigger the release workflow.

# 1. Get the latest version from the CHANGELOG
# This command looks for the first line that starts with '## [' and extracts the version string inside.
$latestVersion = Get-Content -Path CHANGELOG.md | Select-String -Pattern "^## \[(v[0-9]+\.[0-9]+\.[0-9]+)\]" | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -First 1

if (-not $latestVersion) {
    Write-Host "Error: Could not find a version string like '## [v1.0.0]' in CHANGELOG.md"
    exit 1
}

Write-Host "Latest version found: $latestVersion"

# 2. Check for uncommitted changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Uncommitted changes found. Committing..."
    git add .
    git commit -m "Release $latestVersion"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git commit failed. Please resolve the issues and try again."
        exit 1
    }
} else {
    Write-Host "No uncommitted changes."
}

# 3. Create a git tag with the version number
# Use -f to force update the tag if it exists locally, which is useful for testing.
Write-Host "Creating git tag: $latestVersion"
git tag -f $latestVersion

# 4. Push the commit and the tag to the 'master' branch
Write-Host "Pushing commit and tag to origin/master..."
git push origin master
git push origin $latestVersion

Write-Host "Push complete. The GitHub Actions release workflow should now be triggered."
