// PM2 ecosystem config for production deployment
// Run with: pm2 start ecosystem.config.cjs --env production
// Docs: https://pm2.keymetrics.io/docs/usage/application-declaration/

const ROOT_DIR = __dirname;

module.exports = {
  apps: [
    {
      name: "ai-agent-tool",
      script: "./run-production.sh",
      interpreter: "bash",
      cwd: ROOT_DIR,

      // Single process - required because of in-memory SSE broker,
      // AsyncIOScheduler, and SQLite usage. Do NOT change to cluster mode.
      exec_mode: "fork",
      instances: 1,

      // Restart policy
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      min_uptime: "10s",

      // Environment
      env_production: {
        HOST: "0.0.0.0",
        PORT: "8008",
        AI_AGENT_TOOL_SETTINGS_PATH: `${ROOT_DIR}/config/settings.yaml`,
      },

      // Use PM2 default logs (~/.pm2/logs)
      time: true,
    },
  ],
};
