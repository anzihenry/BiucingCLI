import { AnalysisService, Cancellation } from '@biucing/contracts';
import { createHomeModel } from './GeneratedGraph';
export class HomeModel {
  private service: AnalysisService;
  private cancellation: Cancellation = new Cancellation();
  constructor(service: AnalysisService) { this.service = service; }
  async calculate(): Promise<string> { return this.service.analyze(['20', '22'], this.cancellation); }
  close(): Promise<void> { this.cancellation.cancel(); return this.service.close(); }
}
export class HomeFactory {
  private service: AnalysisService;
  constructor(service: AnalysisService) { this.service = service; }
  create(): HomeModel { return createHomeModel(this.service); }
}
