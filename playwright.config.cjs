const path = require("node:path");

const ROOT_DIR = __dirname;
const HOST = process.env.PLAYWRIGHT_HOST || "127.0.0.1";
const PORT = process.env.PLAYWRIGHT_PORT || "8000";
const BASE_URL = `http://${HOST}:${PORT}`;

module.exports = {
  testDir: path.join(ROOT_DIR, "tests", "web"),
  timeout: 60_000,
  reporter: "line",
  use: {
    baseURL: BASE_URL,
  },
  webServer: {
    command: path.join(ROOT_DIR, "scripts", "start-playwright-server.sh"),
    url: `${BASE_URL}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    cwd: ROOT_DIR,
    env: {
      ...process.env,
      HOST,
      PORT,
      PLAYWRIGHT_TMP_DIR: path.join(ROOT_DIR, ".playwright"),
    },
  },
};
