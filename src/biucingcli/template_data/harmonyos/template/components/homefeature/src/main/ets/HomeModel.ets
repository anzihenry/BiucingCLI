import { AnalysisService, Cancellation, CoreError } from '@biucing/contracts';
import { createHomeModel } from './GeneratedGraph';

@Observed
export class HomeModel {
  result: string = 'Ready';
  busy: boolean = false;
  private service: AnalysisService;
  private cancellation: Cancellation = new Cancellation();
  private closed: boolean = false;
  private closing: Promise<void> | undefined = undefined;
  private pending: Promise<void> = Promise.resolve();

  constructor(service: AnalysisService) { this.service = service; }

  calculate(): Promise<string> {
    if (this.closed) { return Promise.reject(new CoreError(4, 'Session is closed')); }
    if (this.busy) { return Promise.reject(new CoreError(1, 'Calculation already running')); }
    this.busy = true;
    const operation = this.performCalculation();
    this.pending = operation.then(() => {}, () => {});
    return operation;
  }

  private async performCalculation(): Promise<string> {
    try {
      const value = await this.service.analyze(['20', '22'], this.cancellation);
      if (!this.closed) { this.result = value; }
      return value;
    } catch (error) {
      if (!this.closed) { this.result = 'Unable to calculate'; }
      throw error as Error;
    } finally {
      this.busy = false;
    }
  }

  close(): Promise<void> {
    if (!this.closing) {
      this.closed = true;
      this.cancellation.cancel();
      this.closing = this.finishClose();
    }
    return this.closing;
  }

  private async finishClose(): Promise<void> {
    try { await this.service.close(); }
    finally { await this.pending; }
  }
}

export class HomeFactory {
  private service: AnalysisService;
  constructor(service: AnalysisService) { this.service = service; }
  create(): HomeModel { return createHomeModel(this.service); }
}
