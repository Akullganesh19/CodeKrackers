# Use the node:24-slim image as requested
FROM node:24-slim AS base

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the Next.js app
RUN npm run build

# Production image
FROM node:24-slim AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy necessary files from build stage
COPY --from=base /app/next.config.mjs ./
COPY --from=base /app/public ./public
COPY --from=base /app/.next ./.next
COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/package.json ./package.json

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
