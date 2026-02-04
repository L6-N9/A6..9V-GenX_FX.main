#!/bin/bash
# Script to push builds to specified Google Cloud projects
# Usage: ./push_to_projects.sh [project-id1] [project-id2] ...

# Default projects
DEFAULT_PROJECTS=("xenon-respect-485202-t0" "positive-mission-51b50" "the-tendril-484308-c0")

# Use arguments if provided, otherwise use defaults
if [ $# -gt 0 ]; then
    PROJECTS=("$@")
else
    PROJECTS=("${DEFAULT_PROJECTS[@]}")
fi

echo "🚀 Starting deployment to ${#PROJECTS[@]} projects..."

for PROJECT in "${PROJECTS[@]}"; do
    echo "----------------------------------------------------------"
    echo "🏗️  Pushing build to project: $PROJECT"
    echo "----------------------------------------------------------"

    # Set the current project
    if ! gcloud config set project "$PROJECT" 2>/dev/null; then
        echo "❌ Failed to set project $PROJECT. Make sure the project ID is correct."
        continue
    fi

    # Attempt to submit the build
    echo "Submitting Cloud Build..."
    if gcloud builds submit --config cloudbuild.yaml .; then
        echo "✅ Successfully submitted build to $PROJECT"
    else
        echo "❌ Failed to submit build to $PROJECT"
        echo "   Possible reasons:"
        echo "   - Not authenticated. Run 'gcloud auth login'."
        echo "   - Cloud Build API not enabled in $PROJECT."
        echo "   - Missing permissions."
    fi
    echo ""
done

echo "🏁 Deployment process finished."
