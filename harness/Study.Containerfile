# Candidate tool/dependency image. Application sources, task contracts, controller
# logs, inference credentials and sealed evaluators are not baked into it.
FROM docker.io/library/node@sha256:21959659f5ad1dbbc4ef0842c3e73d32ab59e95ec10528871e0b1bc56a6dabcd
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git ripgrep python3 make g++ sqlite3 && rm -rf /var/lib/apt/lists/*
RUN npm install --global npm@10.9.0
COPY application-package.json /opt/application-deps/package.json
COPY application-package-lock.json /opt/application-deps/package-lock.json
WORKDIR /opt/application-deps
RUN npm ci && npx playwright install --with-deps chromium && npm cache clean --force
COPY opencode /usr/local/bin/opencode
COPY context-modules /opt/context/node_modules
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
# Move the download made by the root-only build into a readable fixed location.
RUN mv /root/.cache/ms-playwright /opt/playwright-browsers && chmod -R a+rX /opt/playwright-browsers /opt/context /opt/application-deps
ENV CI=1
WORKDIR /workspace
USER node
