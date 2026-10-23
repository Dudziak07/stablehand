#!/usr/bin/env bash
# Creates the target repository the scenario builds a skill for (runs only with --scaffold).
set -euo pipefail

mkdir -p shop-api/src/routes shop-api/src/schemas shop-api/tests

cat > shop-api/package.json <<'EOF'
{
  "name": "shop-api",
  "private": true,
  "type": "module",
  "scripts": { "dev": "tsx src/server.ts", "test": "vitest run" },
  "dependencies": { "express": "^5.1.0", "zod": "^4.1.0" },
  "devDependencies": { "vitest": "^3.2.0", "supertest": "^7.1.0", "tsx": "^4.20.0", "typescript": "^5.9.0" }
}
EOF

cat > shop-api/README.md <<'EOF'
# shop-api

Express API for the shop.

## Conventions
- One router per resource in `src/routes/<resource>.ts`, registered in `src/server.ts`.
- Request bodies are validated with zod schemas in `src/schemas/<resource>.ts`.
- Every route has tests in `tests/<resource>.test.ts` (vitest + supertest).
- Run one test file: `pnpm vitest run tests/<resource>.test.ts`.
EOF

cat > shop-api/src/server.ts <<'EOF'
import express from "express";
import { productsRouter } from "./routes/products.js";

export const app = express();
app.use(express.json());
app.use("/products", productsRouter);
EOF

cat > shop-api/src/schemas/products.ts <<'EOF'
import { z } from "zod";

export const createProduct = z.object({ name: z.string().min(1), priceCents: z.number().int().positive() });
EOF

cat > shop-api/src/routes/products.ts <<'EOF'
import { Router } from "express";
import { createProduct } from "../schemas/products.js";

export const productsRouter = Router();

productsRouter.post("/", (req, res) => {
  const parsed = createProduct.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: parsed.error.issues });
  return res.status(201).json({ id: 1, ...parsed.data });
});
EOF

cat > shop-api/tests/products.test.ts <<'EOF'
import request from "supertest";
import { describe, expect, it } from "vitest";
import { app } from "../src/server.js";

describe("POST /products", () => {
  it("rejects an invalid body", async () => {
    const res = await request(app).post("/products").send({ name: "" });
    expect(res.status).toBe(400);
  });
});
EOF

git -C shop-api init -q
