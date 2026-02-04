import { z } from "zod";
import { pgTable, text, serial, integer, boolean, timestamp, jsonb, real } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

// Resource schema
export const resourceSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  skillLevel: z.enum(["beginner", "intermediate", "advanced"]),
  category: z.enum(["programming", "design", "marketing", "data-science"]),
  resourceType: z.enum(["video", "article", "course", "tutorial"]),
  duration: z.string(),
  imageUrl: z.string(),
  featured: z.boolean().default(false),
  createdAt: z.date().default(() => new Date()),
});

export type Resource = z.infer<typeof resourceSchema>;

// Insert schema (for creating new resources)
export const insertResourceSchema = resourceSchema.omit({
  id: true,
  createdAt: true,
});

export type InsertResource = z.infer<typeof insertResourceSchema>;

// Query filters schema
export const resourceFiltersSchema = z.object({
  search: z.string().optional(),
  skillLevel: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  category: z.enum(["programming", "design", "marketing", "data-science"]).optional(),
  resourceType: z.enum(["video", "article", "course", "tutorial"]).optional(),
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(50).default(12),
});

export type ResourceFilters = z.infer<typeof resourceFiltersSchema>;

// Response schema for paginated resources
export const resourcesResponseSchema = z.object({
  resources: z.array(resourceSchema),
  totalCount: z.number(),
  totalPages: z.number(),
  currentPage: z.number(),
  hasNextPage: z.boolean(),
  hasPrevPage: z.boolean(),
});

export type ResourcesResponse = z.infer<typeof resourcesResponseSchema>;

// --- Drizzle ORM Tables ---

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  email: text("email").notNull().unique(),
  passwordHash: text("password_hash").notNull(),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
  firstName: text("first_name"),
  lastName: text("last_name"),
});

export const tradingAccounts = pgTable("trading_accounts", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  accountName: text("account_name").notNull(),
  broker: text("broker").default("exness"),
  accountId: text("account_id"),
  platform: text("platform"),
  balance: text("balance"),
  currency: text("currency").default("USD"),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
});

export const positions = pgTable("positions", {
  id: serial("id").primaryKey(),
  accountId: integer("account_id").references(() => tradingAccounts.id),
  symbol: text("symbol").notNull(),
  type: text("type").notNull(),
  volume: real("volume").notNull(),
  openPrice: real("open_price").notNull(),
  openTime: timestamp("open_time").notNull(),
  status: text("status").default("open"),
  profit: real("profit"),
});

export const notifications = pgTable("notifications", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  title: text("title").notNull(),
  message: text("message").notNull(),
  read: boolean("read").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

export const educationalResources = pgTable("educational_resources", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  skillLevel: text("skill_level"),
  category: text("category"),
  resourceType: text("resource_type"),
  duration: text("duration"),
  imageUrl: text("image_url"),
  featured: boolean("featured").default(false),
  createdAt: timestamp("created_at").defaultNow(),
  url: text("url"),
  tags: jsonb("tags"),
  rating: text("rating"),
});

export const tradingBots = pgTable("trading_bots", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  accountId: integer("account_id").references(() => tradingAccounts.id),
  name: text("name").notNull(),
  strategy: text("strategy").notNull(),
  symbols: jsonb("symbols"),
  parameters: jsonb("parameters"),
  status: text("status").default("stopped"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  tradingAccounts: many(tradingAccounts),
  notifications: many(notifications),
}));

export const tradingAccountsRelations = relations(tradingAccounts, ({ one, many }) => ({
  user: one(users, {
    fields: [tradingAccounts.userId],
    references: [users.id],
  }),
  positions: many(positions),
}));
