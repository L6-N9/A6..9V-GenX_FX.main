
#!/bin/bash

# Create clean directory structure
mkdir -p {client,server,shared,python,scripts}

# Move client files from the cleanest version (Gendollardollar/client)
if [ -d "Gendollardollar/client" ]; then
  cp -r Gendollardollar/client/* client/
fi

# Move server files from Gendollardollar/server
if [ -d "Gendollardollar/server" ]; then
  cp -r Gendollardollar/server/* server/
fi

# Move shared schema
if [ -f "Gendollardollar/server/shared/schema.ts" ]; then
  cp Gendollardollar/server/shared/schema.ts shared/
fi

# Consolidate Python files
if [ -d "GenZ-main/python" ]; then
  cp -r GenZ-main/python/* python/
fi
if [ -d "GenZ-main/GenZ-main/python" ]; then
  cp -r GenZ-main/GenZ-main/python/* python/
fi

# Move configuration files to root
cp Gendollardollar/package.json .
cp Gendollardollar/tsconfig.json .
cp Gendollardollar/vite.config.ts .
cp Gendollardollar/tailwind.config.ts .
cp Gendollardollar/postcss.config.js .
cp Gendollardollar/components.json .
cp Gendollardollar/drizzle.config.ts .

# Create .env.example from GenZ-main
if [ -f "GenZ-main/.env.example" ]; then
  cp GenZ-main/.env.example .
fi

echo "Project reorganization complete!"
