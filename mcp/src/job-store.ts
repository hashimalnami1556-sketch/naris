import type { NarisJob } from "./types.js";

export class InMemoryJobStore {
  private readonly jobs = new Map<string, NarisJob>();

  create(job: NarisJob): NarisJob {
    this.jobs.set(job.job_id, job);
    return job;
  }

  get(jobId: string): NarisJob | undefined {
    return this.jobs.get(jobId);
  }

  list(): NarisJob[] {
    return [...this.jobs.values()];
  }
}
