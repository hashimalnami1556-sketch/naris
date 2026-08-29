export type NarisPermission = "project.read" | "asset.read" | "validation.run" | "asset.build" | "asset.export" | "admin";

const LEVEL: Record<NarisPermission, number> = {
  "project.read": 0,
  "asset.read": 0,
  "validation.run": 1,
  "asset.build": 2,
  "asset.export": 3,
  admin: 4,
};

export function hasPermission(granted: NarisPermission[], required: NarisPermission): boolean {
  return granted.some((permission) => permission === "admin" || LEVEL[permission] >= LEVEL[required]);
}
