export class ServiceRegistry {
  private services = new Map<string, unknown>();
  set<T>(key: string, service: T): void { this.services.set(key, service); }
  get<T>(key: string): T {
    const service = this.services.get(key);
    if (!service) throw new Error(`NARIS service not registered: ${key}`);
    return service as T;
  }
  has(key: string): boolean { return this.services.has(key); }
}
